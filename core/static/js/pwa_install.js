(function () {
  const PWA_INSTALL_BANNER_DISMISS_KEY = "finhub_pwa_install_banner_dismissed_v1";
  const DEFAULT_INSTALL_RELEASE_CODE = "dashboard-instalacao-app-2026-04";
  const RUNTIME_KEY = "__finhubPwaInstallRuntimeV1";

  function onReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }
    callback();
  }

  function getStandaloneState() {
    const mediaStandalone = typeof window.matchMedia === "function" && window.matchMedia("(display-mode: standalone)").matches;
    const iosStandalone = Boolean(window.navigator && window.navigator.standalone === true);
    return Boolean(mediaStandalone || iosStandalone);
  }

  function readRuntimeConfig() {
    const defaults = {
      enabled: true,
      service_worker_enabled: true,
      service_worker_url: "/service-worker.js",
      is_development: false,
    };

    let payload = null;
    const jsonElement = document.getElementById("finhub-pwa-runtime-config");
    if (jsonElement) {
      try {
        payload = JSON.parse(jsonElement.textContent || "{}");
      } catch (error) {
        payload = null;
      }
    }

    const windowPayload = window.finhubPwaRuntimeConfig;
    const merged = Object.assign({}, defaults, payload || {}, windowPayload || {});
    merged.enabled = Boolean(merged.enabled);
    merged.service_worker_enabled = Boolean(merged.service_worker_enabled);
    merged.is_development = Boolean(merged.is_development);
    merged.service_worker_url = `${merged.service_worker_url || ""}`.trim() || defaults.service_worker_url;
    return merged;
  }

  function createRuntimeState() {
    return {
      hasDeferredPrompt: false,
      deferredPromptEvent: null,
      isStandalone: getStandaloneState(),
      listenersBound: false,
      swRegistrationStarted: false,
      subscribers: [],
    };
  }

  function getRuntimeState() {
    const existing = window[RUNTIME_KEY];
    if (existing && typeof existing === "object") {
      if (!Array.isArray(existing.subscribers)) {
        existing.subscribers = [];
      }
      if (typeof existing.hasDeferredPrompt !== "boolean") {
        existing.hasDeferredPrompt = Boolean(existing.deferredPromptEvent);
      }
      if (typeof existing.isStandalone !== "boolean") {
        existing.isStandalone = getStandaloneState();
      }
      return existing;
    }
    const created = createRuntimeState();
    window[RUNTIME_KEY] = created;
    return created;
  }

  const runtime = getRuntimeState();
  const pwaRuntimeConfig = readRuntimeConfig();

  window.finhubPwaInstallDebug = {
    getState: function () {
      return {
        hasDeferredPrompt: Boolean(runtime.hasDeferredPrompt && runtime.deferredPromptEvent),
        isStandalone: Boolean(runtime.isStandalone),
        listenersBound: Boolean(runtime.listenersBound),
        swRegistrationStarted: Boolean(runtime.swRegistrationStarted),
        platform: runtime.platform || null,
        flow: runtime.flow || null,
      };
    },
  };

  function notifyRuntimeSubscribers() {
    const subscribers = Array.isArray(runtime.subscribers) ? runtime.subscribers.slice() : [];
    subscribers.forEach(function (subscriber) {
      if (typeof subscriber !== "function") return;
      try {
        subscriber(runtime);
      } catch (error) {
        console.warn("[pwa] falha ao notificar atualização de estado de instalação.", error);
      }
    });
  }

  function subscribeToRuntime(subscriber) {
    if (typeof subscriber !== "function") return function () {};
    runtime.subscribers.push(subscriber);
    return function unsubscribe() {
      runtime.subscribers = runtime.subscribers.filter(function (item) {
        return item !== subscriber;
      });
    };
  }

  function bindInstallabilityListeners() {
    if (runtime.listenersBound) return;

    window.addEventListener("beforeinstallprompt", function (event) {
      event.preventDefault();
      runtime.deferredPromptEvent = event;
      runtime.hasDeferredPrompt = true;
      runtime.isStandalone = getStandaloneState();
      notifyRuntimeSubscribers();
    });

    window.addEventListener("appinstalled", function () {
      runtime.deferredPromptEvent = null;
      runtime.hasDeferredPrompt = false;
      runtime.isStandalone = true;
      notifyRuntimeSubscribers();
    });

    runtime.listenersBound = true;
  }

  function registerServiceWorkerOnce() {
    if (!pwaRuntimeConfig.service_worker_enabled) return;
    if (!("serviceWorker" in navigator)) return;
    if (runtime.swRegistrationStarted) return;
    runtime.swRegistrationStarted = true;

    navigator.serviceWorker.register(pwaRuntimeConfig.service_worker_url).catch(function (error) {
      console.warn("[pwa] falha ao registrar service worker.", error);
    });
  }

  function registrationUsesFinancesServiceWorker(registration) {
    if (!registration || typeof registration !== "object") return false;
    const candidates = [registration.active, registration.waiting, registration.installing];
    return candidates.some(function (worker) {
      if (!worker || !worker.scriptURL) return false;
      try {
        const scriptPath = new URL(worker.scriptURL, window.location.origin).pathname;
        return scriptPath.endsWith("/service-worker.js");
      } catch (error) {
        return false;
      }
    });
  }

  function cleanupLegacyServiceWorkerAndCaches() {
    if ("serviceWorker" in navigator && typeof navigator.serviceWorker.getRegistrations === "function") {
      navigator.serviceWorker
        .getRegistrations()
        .then(function (registrations) {
          registrations.forEach(function (registration) {
            if (!registrationUsesFinancesServiceWorker(registration)) return;
            registration.unregister().catch(function () {
              return null;
            });
          });
        })
        .catch(function () {
          return null;
        });
    }

    if (!("caches" in window) || typeof window.caches.keys !== "function") return;
    window.caches
      .keys()
      .then(function (keys) {
        return Promise.all(
          keys
            .filter(function (key) {
              return `${key || ""}`.startsWith("finances-hub-");
            })
            .map(function (key) {
              return window.caches.delete(key).catch(function () {
                return null;
              });
            }),
        );
      })
      .catch(function () {
        return null;
      });
  }

  function getSafeLocalStorage() {
    try {
      return window.localStorage || null;
    } catch (error) {
      return null;
    }
  }

  function readJsonScriptElement(id) {
    const element = document.getElementById(id);
    if (!element) return null;
    try {
      return JSON.parse(element.textContent || "{}");
    } catch (error) {
      return null;
    }
  }

  function normalizeReleaseCode(value) {
    return `${value || ""}`.trim();
  }

  function hasPendingInstallRelease(payload, releaseCode) {
    if (!payload || !Array.isArray(payload.releases)) return true;
    const targetCode = normalizeReleaseCode(releaseCode);
    if (!targetCode) return true;
    return payload.releases.some(function (release) {
      return normalizeReleaseCode(release && release.code) === targetCode;
    });
  }

  function waitForDeferredPromptAvailability(timeoutMs) {
    return new Promise(function (resolve) {
      if (runtime.hasDeferredPrompt && runtime.deferredPromptEvent) {
        resolve(true);
        return;
      }

      const startedAt = Date.now();
      const intervalId = window.setInterval(function () {
        if (runtime.hasDeferredPrompt && runtime.deferredPromptEvent) {
          window.clearInterval(intervalId);
          resolve(true);
          return;
        }

        if (Date.now() - startedAt >= timeoutMs) {
          window.clearInterval(intervalId);
          resolve(false);
        }
      }, 120);
    });
  }

  if (!pwaRuntimeConfig.enabled) {
    cleanupLegacyServiceWorkerAndCaches();
    return;
  }

  bindInstallabilityListeners();
  if (pwaRuntimeConfig.service_worker_enabled) {
    registerServiceWorkerOnce();
  } else {
    cleanupLegacyServiceWorkerAndCaches();
  }

  onReady(function () {
    const utils = window.financesPwaInstallUtils;
    if (!utils || typeof utils.detectPlatform !== "function") return;

    const root = document.querySelector("[data-pwa-footer]");
    const footerLabel = document.querySelector("[data-pwa-footer-label]");
    const footerTrigger = document.querySelector("[data-pwa-install-trigger]");
    const status = document.querySelector("[data-pwa-install-status]");
    const modal = document.querySelector("[data-pwa-helper-modal]");
    const modalTitle = document.querySelector("[data-pwa-helper-title]");
    const modalDescription = document.querySelector("[data-pwa-helper-description]");
    const modalSteps = document.querySelector("[data-pwa-helper-steps]");
    const modalCloseButtons = Array.from(document.querySelectorAll("[data-pwa-helper-close]"));

    const installBanner = document.querySelector("[data-pwa-install-banner]");
    const bannerTrigger = installBanner ? installBanner.querySelector("[data-pwa-install-banner-trigger]") : null;
    const bannerDismissButton = installBanner ? installBanner.querySelector("[data-pwa-install-banner-dismiss]") : null;
    const bannerDescription = installBanner ? installBanner.querySelector("[data-pwa-install-banner-description]") : null;

    if (!root || !footerTrigger || !status) return;

    const dashboardReleasePayload = readJsonScriptElement("dashboard-release-payload-data");
    const bannerReleaseCode = normalizeReleaseCode(
      installBanner && installBanner.dataset && installBanner.dataset.pwaReleaseCode,
    ) || DEFAULT_INSTALL_RELEASE_CODE;

    const bannerShouldTrackRelease = hasPendingInstallRelease(dashboardReleasePayload, bannerReleaseCode);
    const storage = getSafeLocalStorage();
    let bannerDismissedByUser = storage ? storage.getItem(PWA_INSTALL_BANNER_DISMISS_KEY) === "1" : false;

    const platform = utils.detectPlatform(window.navigator && window.navigator.userAgent);
    const isMobileContext = typeof utils.isMobilePlatform === "function"
      ? utils.isMobilePlatform(platform)
      : platform === utils.PLATFORM.ANDROID || platform === utils.PLATFORM.IOS;
    let hasDeferredPrompt = Boolean(runtime.hasDeferredPrompt && runtime.deferredPromptEvent);
    let deferredPromptEvent = runtime.deferredPromptEvent;
    let isStandalone = Boolean(runtime.isStandalone || getStandaloneState());

    function syncStateFromRuntime() {
      hasDeferredPrompt = Boolean(runtime.hasDeferredPrompt && runtime.deferredPromptEvent);
      deferredPromptEvent = runtime.deferredPromptEvent;
      isStandalone = Boolean(runtime.isStandalone || getStandaloneState());
    }

    syncStateFromRuntime();

    function setTriggerDisabled(element, disabled) {
      if (!element) return;
      const shouldDisable = Boolean(disabled);
      const isButton = element.tagName === "BUTTON";
      if (isButton) {
        element.disabled = shouldDisable;
      }
      element.setAttribute("aria-disabled", shouldDisable ? "true" : "false");
      if (!isButton) {
        if (shouldDisable) {
          element.setAttribute("tabindex", "-1");
        } else {
          element.removeAttribute("tabindex");
        }
      }
    }

    function setModalContent(content) {
      if (!modalTitle || !modalDescription || !modalSteps) return;
      modalTitle.textContent = content.title || "Instalar app";
      modalDescription.textContent = content.description || "";
      modalSteps.textContent = "";
      const steps = Array.isArray(content.steps) ? content.steps : [];
      steps.forEach(function (step) {
        const item = document.createElement("li");
        item.textContent = `${step || ""}`.trim();
        if (!item.textContent) return;
        modalSteps.appendChild(item);
      });
    }

    function openModal() {
      if (!modal) return;
      modal.classList.remove("hidden");
      modal.setAttribute("aria-hidden", "false");
    }

    function closeModal() {
      if (!modal) return;
      modal.classList.add("hidden");
      modal.setAttribute("aria-hidden", "true");
    }

    function dispatchInstallEvent(name) {
      if (typeof window.CustomEvent !== "function") return;
      window.dispatchEvent(
        new window.CustomEvent(name, {
          detail: {
            releaseCode: bannerReleaseCode,
          },
        }),
      );
    }

    function persistBannerDismissed(dismissed) {
      if (!storage) return;
      if (dismissed) {
        storage.setItem(PWA_INSTALL_BANNER_DISMISS_KEY, "1");
        return;
      }
      storage.removeItem(PWA_INSTALL_BANNER_DISMISS_KEY);
    }

    function dismissInstallBanner() {
      bannerDismissedByUser = true;
      persistBannerDismissed(true);
      applyUiState();
      dispatchInstallEvent("finhub:pwa-install-banner-dismissed");
    }

    function applyInstallBannerUi(flow) {
      if (!installBanner || !bannerTrigger) return;
      const bannerMode = utils.resolveInstallBannerMode({
        flow: flow,
        platform: platform,
        isStandalone: isStandalone,
        isDismissedByUser: bannerDismissedByUser,
        hasPendingInstallRelease: bannerShouldTrackRelease,
      });

      installBanner.dataset.pwaBannerMode = bannerMode;
      if (bannerMode === utils.BANNER_MODE.HIDDEN) {
        installBanner.classList.add("hidden");
        return;
      }

      installBanner.classList.remove("hidden");
      if (bannerMode === utils.BANNER_MODE.IOS_GUIDE) {
        bannerTrigger.textContent = "Como adicionar";
        if (bannerDescription) {
          bannerDescription.textContent = "No iPhone, use Adicionar à Tela de Início para abrir como app.";
        }
      } else {
        bannerTrigger.textContent = "Instalar";
        if (bannerDescription) {
          bannerDescription.textContent = "Ao tocar em instalar, o navegador abre o popup nativo para adicionar o app.";
        }
      }
      setTriggerDisabled(bannerTrigger, flow === utils.FLOW.INSTALLED);
    }

    function applyUiState() {
      const flow = utils.resolveInstallFlow({
        platform: platform,
        isStandalone: isStandalone,
        hasDeferredPrompt: hasDeferredPrompt,
      });
      const footerCtaLabel = utils.resolveCtaLabel({ flow: flow, platform: platform });
      const guide = utils.resolveGuideContent({ flow: flow, platform: platform });

      root.dataset.pwaPlatform = platform;
      root.dataset.pwaFlow = flow;
      root.dataset.pwaMobile = isMobileContext ? "true" : "false";
      runtime.platform = platform;
      runtime.flow = flow;
      if (isMobileContext) {
        if (footerLabel) {
          footerLabel.textContent = "Use o Finances Hub como app no seu celular.";
        }
        footerTrigger.classList.remove("hidden");
        footerTrigger.textContent = footerCtaLabel || "Instalar app";
        setTriggerDisabled(footerTrigger, flow === utils.FLOW.INSTALLED);
      } else {
        if (footerLabel) {
          footerLabel.textContent = "Instalação do app disponível para dispositivos móveis.";
        }
        footerTrigger.classList.add("hidden");
        footerTrigger.textContent = "";
        setTriggerDisabled(footerTrigger, true);
      }
      applyInstallBannerUi(flow);

      if (flow === utils.FLOW.INSTALLED) {
        status.textContent = "Este app já está instalado neste dispositivo.";
      } else if (flow === utils.FLOW.NATIVE_PROMPT) {
        status.textContent = "Toque em instalar para abrir o popup nativo do navegador.";
      } else if (flow === utils.FLOW.IOS_INSTRUCTIONS) {
        status.textContent = "No iPhone, use Adicionar à Tela de Início.";
      } else if (flow === utils.FLOW.ANDROID_PROMPT_UNAVAILABLE) {
        status.textContent = "Instalação automática indisponível neste Android (prompt nativo não disponível).";
      } else if (flow === utils.FLOW.DESKTOP_INFO) {
        status.textContent = "Instalação do app disponível para dispositivos móveis.";
      } else {
        status.textContent = "Instalação indisponível neste navegador/dispositivo.";
      }
      setModalContent(guide);
    }

    async function handleNativePrompt() {
      const promptEvent = deferredPromptEvent || runtime.deferredPromptEvent;
      if (!promptEvent || typeof promptEvent.prompt !== "function") {
        return { opened: false, outcome: null };
      }

      promptEvent.prompt();

      let outcome = null;
      try {
        if (promptEvent.userChoice && typeof promptEvent.userChoice.then === "function") {
          const choiceResult = await promptEvent.userChoice;
          outcome = `${choiceResult && choiceResult.outcome ? choiceResult.outcome : ""}`.trim().toLowerCase() || null;
        }
      } catch (error) {
        console.warn("[pwa] erro ao aguardar resposta do prompt de instalação.", error);
      } finally {
        if (runtime.deferredPromptEvent === promptEvent) {
          runtime.deferredPromptEvent = null;
        }
        runtime.hasDeferredPrompt = Boolean(runtime.deferredPromptEvent);
        runtime.isStandalone = getStandaloneState();
        notifyRuntimeSubscribers();
      }

      if (outcome === "dismissed") {
        bannerDismissedByUser = true;
        persistBannerDismissed(true);
        dispatchInstallEvent("finhub:pwa-install-banner-dismissed");
      }

      syncStateFromRuntime();
      applyUiState();
      return { opened: true, outcome: outcome };
    }

    async function tryOpenNativeInstall() {
      syncStateFromRuntime();
      if (hasDeferredPrompt && deferredPromptEvent) {
        return handleNativePrompt();
      }

      if (platform !== utils.PLATFORM.ANDROID) {
        return { opened: false, outcome: null };
      }

      const becameAvailable = await waitForDeferredPromptAvailability(1800);
      if (!becameAvailable) {
        syncStateFromRuntime();
        return { opened: false, outcome: null };
      }

      syncStateFromRuntime();
      if (!hasDeferredPrompt || !deferredPromptEvent) {
        return { opened: false, outcome: null };
      }
      return handleNativePrompt();
    }

    async function onInstallTriggerClick(event) {
      event.preventDefault();
      const target = event.currentTarget;
      if (target && target.getAttribute("aria-disabled") === "true") return;
      if (!isMobileContext) return;

      const nativePromptResult = await tryOpenNativeInstall();
      if (nativePromptResult.opened) return;

      openModal();
    }

    const unsubscribeRuntime = subscribeToRuntime(function () {
      syncStateFromRuntime();
      applyUiState();
    });

    window.addEventListener("appinstalled", function () {
      bannerDismissedByUser = false;
      persistBannerDismissed(false);
      syncStateFromRuntime();
      applyUiState();
      dispatchInstallEvent("finhub:pwa-install-completed");
    });

    footerTrigger.addEventListener("click", onInstallTriggerClick);
    if (bannerTrigger) {
      bannerTrigger.addEventListener("click", onInstallTriggerClick);
    }
    if (bannerDismissButton) {
      bannerDismissButton.addEventListener("click", function (event) {
        event.preventDefault();
        dismissInstallBanner();
      });
    }

    modalCloseButtons.forEach(function (button) {
      button.addEventListener("click", closeModal);
    });

    if (modal) {
      modal.addEventListener("click", function (event) {
        if (event.target === modal) closeModal();
      });
    }

    window.addEventListener("beforeunload", function () {
      unsubscribeRuntime();
    }, { once: true });

    applyUiState();
  });
})();
