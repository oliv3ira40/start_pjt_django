(function () {
  const DRIVER_GLOBAL_KEY = "driver";
  const baseScript = document.currentScript || document.querySelector('script[data-onboarding-driver-base="1"]');
  const configuredJsPath = `${baseScript?.dataset?.driverjsJsPath || ""}`.trim();
  const configuredCssPath = `${baseScript?.dataset?.driverjsCssPath || ""}`.trim();
  const ASSETS = {
    jsPath: configuredJsPath || "/static/vendor/driverjs/driver.js",
    cssPath: configuredCssPath || "/static/vendor/driverjs/driver.css",
  };
  let loadingPromise = null;

  function resolveDriverFactory() {
    const driverGlobal = window[DRIVER_GLOBAL_KEY];
    if (!driverGlobal) return null;
    if (typeof driverGlobal.js === "function") return driverGlobal.js;
    if (driverGlobal.js && typeof driverGlobal.js.driver === "function") return driverGlobal.js.driver;
    if (typeof driverGlobal.driver === "function") return driverGlobal.driver;
    return null;
  }

  function hasDriverLoaded() {
    return Boolean(resolveDriverFactory());
  }

  function ensureCssLoaded() {
    const existingLink = document.querySelector(`link[data-driverjs-base="1"]`);
    if (existingLink) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = ASSETS.cssPath;
    link.dataset.driverjsBase = "1";
    document.head.appendChild(link);
  }

  function ensureScriptLoaded() {
    return new Promise((resolve, reject) => {
      const existingScript = document.querySelector('script[data-driverjs-base="1"]');
      if (existingScript) {
        existingScript.addEventListener("load", resolve, { once: true });
        existingScript.addEventListener("error", reject, { once: true });
        if (hasDriverLoaded()) resolve();
        return;
      }

      const script = document.createElement("script");
      script.src = ASSETS.jsPath;
      script.defer = true;
      script.dataset.driverjsBase = "1";
      script.addEventListener("load", resolve, { once: true });
      script.addEventListener("error", reject, { once: true });
      document.head.appendChild(script);
    });
  }

  async function ensureDriverReady() {
    if (hasDriverLoaded()) return;
    if (!loadingPromise) {
      ensureCssLoaded();
      loadingPromise = ensureScriptLoaded();
    }
    await loadingPromise;
  }

  function createDriverInstance(options = {}) {
    const driverFactory = resolveDriverFactory();
    if (!driverFactory) return null;
    return driverFactory(options);
  }

  const onboardingDriverBase = {
    assets: ASSETS,
    hasDriverLoaded,
    ensureDriverReady,
    createDriverInstance,
  };
  window.onboardingDriverBase = onboardingDriverBase;
  window.financesOnboardingDriverBase = onboardingDriverBase;
})();
