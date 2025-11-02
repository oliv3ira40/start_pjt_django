from __future__ import annotations

import logging
import math
import os
import platform
import shutil
import socket
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from django.core.cache import caches

from .models import SystemHealthConfig

logger = logging.getLogger(__name__)

CACHE_KEY = "syshealth:metrics"
DEFAULT_CACHE_SECONDS = 15
TIMEZONE = ZoneInfo("America/Sao_Paulo")


@dataclass
class Thresholds:
    warn_cpu_load_per_core: float = 0.7
    crit_cpu_load_per_core: float = 1.0
    warn_mem_used_pct: int = 80
    crit_mem_used_pct: int = 90
    warn_disk_used_pct: int = 80
    crit_disk_used_pct: int = 90


STATUS_LABELS = {
    "ok": "OK",
    "warn": "Atenção",
    "crit": "Crítico",
    "unknown": "N/D",
}


def get_system_health_snapshot(force_refresh: bool = False) -> Dict[str, Any]:
    cache = caches["default"]
    if not force_refresh:
        cached = cache.get(CACHE_KEY)
        if cached is not None:
            return cached

    config = SystemHealthConfig.objects.first()
    thresholds = Thresholds()
    cache_seconds = DEFAULT_CACHE_SECONDS
    if config:
        thresholds = Thresholds(
            warn_cpu_load_per_core=config.warn_cpu_load_per_core,
            crit_cpu_load_per_core=config.crit_cpu_load_per_core,
            warn_mem_used_pct=config.warn_mem_used_pct,
            crit_mem_used_pct=config.crit_mem_used_pct,
            warn_disk_used_pct=config.warn_disk_used_pct,
            crit_disk_used_pct=config.crit_disk_used_pct,
        )
        cache_seconds = max(config.cache_seconds, 1)

    snapshot = collect_metrics(thresholds)
    snapshot["cache_seconds"] = cache_seconds
    cache.set(CACHE_KEY, snapshot, cache_seconds)
    return snapshot


def collect_metrics(thresholds: Thresholds) -> Dict[str, Any]:
    hostname = socket.gethostname()
    system_platform = platform.platform()
    kernel = platform.release()
    python_version = platform.python_version()
    local_time = datetime.now(TIMEZONE)

    cpu_info = collect_cpu_info(thresholds)
    memory_info = collect_memory_info(thresholds)
    disk_info = collect_disk_info(thresholds)
    uptime_info = collect_uptime_info()

    summary_lines = [
        f"Host: {hostname}",
        f"SO: {system_platform}",
        f"Kernel: {kernel}",
        f"Python: {python_version}",
        f"CPU: núcleos={cpu_info['cores_display']}, load={cpu_info['load_display']}, load/núcleo={cpu_info['load_per_core_display']} ({cpu_info['status_label']})",
        f"Memória: total={memory_info['total_display']}, usado={memory_info['used_display']} ({memory_info['percent_display']}) ({memory_info['status_label']})",
        f"Disco '/': total={disk_info['total_display']}, usado={disk_info['used_display']} ({disk_info['percent_display']}), livre={disk_info['free_display']} ({disk_info['status_label']})",
        f"Uptime: {uptime_info['display']}",
        f"Atualizado em: {local_time.strftime('%d/%m/%Y %H:%M:%S')}",
    ]

    return {
        "hostname": hostname,
        "system_platform": system_platform,
        "kernel": kernel,
        "python_version": python_version,
        "local_time": local_time,
        "cpu": cpu_info,
        "memory": memory_info,
        "disk": disk_info,
        "uptime": uptime_info,
        "summary_text": "\n".join(summary_lines),
    }


def collect_cpu_info(thresholds: Thresholds) -> Dict[str, Any]:
    cores = os.cpu_count()
    load_values: Optional[tuple[float, float, float]] = None
    try:
        load_values = os.getloadavg()
    except (AttributeError, OSError):
        logger.warning("os.getloadavg() não disponível; exibindo N/D para carga de CPU.")

    load_per_core = None
    if load_values and cores:
        try:
            load_per_core = load_values[0] / cores if cores else None
        except ZeroDivisionError:  # pragma: no cover - defensive
            load_per_core = None

    status = determine_status(load_per_core, thresholds.warn_cpu_load_per_core, thresholds.crit_cpu_load_per_core)

    return {
        "cores": cores,
        "cores_display": str(cores) if cores is not None else "N/D",
        "load": load_values,
        "load_display": format_load_values(load_values),
        "load_per_core": load_per_core,
        "load_per_core_display": f"{load_per_core:.2f}" if load_per_core is not None else "N/D",
        "status": status,
        "status_label": STATUS_LABELS[status],
    }


def collect_memory_info(thresholds: Thresholds) -> Dict[str, Any]:
    meminfo = read_meminfo()
    if not meminfo:
        return {
            "total": None,
            "used": None,
            "percent": None,
            "total_display": "N/D",
            "used_display": "N/D",
            "percent_display": "N/D",
            "status": "unknown",
            "status_label": STATUS_LABELS["unknown"],
        }

    total = meminfo.get("MemTotal")
    available = meminfo.get("MemAvailable")
    if total is None or available is None:
        logger.warning("Valores de memória incompletos em /proc/meminfo; exibindo N/D.")
        return {
            "total": None,
            "used": None,
            "percent": None,
            "total_display": "N/D",
            "used_display": "N/D",
            "percent_display": "N/D",
            "status": "unknown",
            "status_label": STATUS_LABELS["unknown"],
        }

    used = total - available
    percent = (used / total * 100) if total else None
    status = determine_status(percent, thresholds.warn_mem_used_pct, thresholds.crit_mem_used_pct)

    return {
        "total": total,
        "used": used,
        "percent": percent,
        "total_display": format_bytes(total),
        "used_display": format_bytes(used),
        "percent_display": format_percent(percent),
        "status": status,
        "status_label": STATUS_LABELS[status],
    }


def collect_disk_info(thresholds: Thresholds) -> Dict[str, Any]:
    try:
        usage = shutil.disk_usage("/")
    except OSError:
        logger.warning("Não foi possível ler o uso de disco do diretório raiz.")
        return {
            "total": None,
            "used": None,
            "free": None,
            "percent": None,
            "total_display": "N/D",
            "used_display": "N/D",
            "free_display": "N/D",
            "percent_display": "N/D",
            "status": "unknown",
            "status_label": STATUS_LABELS["unknown"],
        }

    total = usage.total
    used = usage.used
    free = usage.free
    percent = (used / total * 100) if total else None
    status = determine_status(percent, thresholds.warn_disk_used_pct, thresholds.crit_disk_used_pct)

    return {
        "total": total,
        "used": used,
        "free": free,
        "percent": percent,
        "total_display": format_bytes(total),
        "used_display": format_bytes(used),
        "free_display": format_bytes(free),
        "percent_display": format_percent(percent),
        "status": status,
        "status_label": STATUS_LABELS[status],
    }


def collect_uptime_info() -> Dict[str, Any]:
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as uptime_file:
            raw_value = uptime_file.readline().split()[0]
            seconds = float(raw_value)
    except (OSError, ValueError, IndexError):
        logger.warning("Não foi possível ler o uptime do sistema.")
        return {
            "seconds": None,
            "display": "N/D",
        }

    return {
        "seconds": seconds,
        "display": format_duration(seconds),
    }


def determine_status(value: Optional[float], warn_threshold: float, crit_threshold: float) -> str:
    if value is None:
        return "unknown"
    if value >= crit_threshold:
        return "crit"
    if value >= warn_threshold:
        return "warn"
    return "ok"


def format_load_values(values: Optional[tuple[float, float, float]]) -> str:
    if not values:
        return "N/D"
    return " / ".join(f"{val:.2f}" for val in values)


def format_bytes(value: Optional[int]) -> str:
    if value is None:
        return "N/D"
    if value == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    magnitude = min(int(math.log(value, 1024)), len(units) - 1)
    scaled = value / (1024 ** magnitude)
    if magnitude == 0:
        return f"{int(value)} {units[magnitude]}"
    return f"{scaled:.2f} {units[magnitude]}"


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "N/D"
    return f"{value:.1f}%"


def format_duration(seconds: float) -> str:
    if seconds is None:
        return "N/D"
    delta = timedelta(seconds=int(seconds))
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days} dia{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hora{'s' if hours != 1 else ''}")
    if minutes or not parts:
        parts.append(f"{minutes} minuto{'s' if minutes != 1 else ''}")
    return ", ".join(parts)


def read_meminfo() -> Optional[Dict[str, int]]:
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as meminfo_file:
            lines = meminfo_file.readlines()
    except OSError:
        logger.warning("Não foi possível ler /proc/meminfo.")
        return None

    data: Dict[str, int] = {}
    for line in lines:
        try:
            key, value, *_ = line.split()
            data[key.rstrip(":")] = int(value) * 1024
        except ValueError:
            continue
    return data
