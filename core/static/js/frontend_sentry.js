(function () {
  const configNode = document.querySelector("[data-frontend-sentry-config]");
  if (!configNode) return;

  const enabled = configNode.dataset.enabled === "true";
  const reportUrl = configNode.dataset.reportUrl || "";
  const environment = configNode.dataset.environment || "development";
  const release = configNode.dataset.release || "";
  if (!enabled || !reportUrl) return;

  function sanitizeMessage(value) {
    return String(value || "")
      .replace(/https?:\/\/[^\s]+/g, "[url]")
      .replace(/[A-Za-z0-9_-]{32,}/g, "[token]")
      .slice(0, 240);
  }

  function sendReport(payload) {
    const body = JSON.stringify({
      type: String(payload.type || "javascript_error").slice(0, 80),
      message: sanitizeMessage(payload.message || "Erro JavaScript no front-end."),
      path: window.location.pathname || "",
      mode: document.querySelector("[data-shopping-trip-app]")?.dataset.mode || "",
      feature: String(payload.feature || "").slice(0, 80),
      reason: String(payload.reason || "").slice(0, 100),
      environment,
      release,
    });
    try {
      if (window.navigator?.sendBeacon) {
        const blob = new Blob([body], { type: "application/json" });
        if (window.navigator.sendBeacon(reportUrl, blob)) return;
      }
      window.fetch(reportUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        keepalive: true,
        body,
      }).catch(() => {});
    } catch (_error) {
      // Error reporting must never break the app.
    }
  }

  window.financesFrontendSentry = {
    captureException(error, context) {
      sendReport({
        type: "manual_capture",
        message: error?.message || String(error || "Erro no front-end."),
        feature: context?.feature || "",
        reason: context?.reason || "",
      });
    },
  };

  window.addEventListener("error", (event) => {
    sendReport({
      type: "javascript_error",
      message: event?.message || event?.error?.message || "Erro JavaScript não capturado.",
      feature: "global_error",
    });
  });

  window.addEventListener("unhandledrejection", (event) => {
    const reason = event?.reason;
    sendReport({
      type: "unhandled_rejection",
      message: reason?.message || String(reason || "Promise rejeitada no front-end."),
      feature: "global_promise",
    });
  });
})();
