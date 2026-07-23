(function () {
  "use strict";

  const VALID_THEME_MODES = new Set(["light", "dark", "auto"]);

  function normalizeThemeMode(mode) {
    if (typeof mode !== "string") return "light";
    const normalized = mode.trim().toLowerCase();
    return VALID_THEME_MODES.has(normalized) ? normalized : "light";
  }

  function readCsrfTokenFromCookie() {
    const cookie = document.cookie || "";
    const parts = cookie.split(";");
    for (const part of parts) {
      const segment = part.trim();
      if (!segment.startsWith("financeshub_csrftoken=")) continue;
      return decodeURIComponent(segment.slice("financeshub_csrftoken=".length));
    }
    return "";
  }

  function readCurrentThemeMode() {
    try {
      const fromStorage = normalizeThemeMode(window.localStorage.getItem("theme") || "");
      if (VALID_THEME_MODES.has(fromStorage)) return fromStorage;
    } catch (error) {
      // localStorage access can fail; fall back to dataset.
    }
    return normalizeThemeMode(document.documentElement.dataset.theme || "light");
  }

  async function persistThemeMode(mode) {
    const endpoint = window.finhubThemePreferenceSaveUrl;
    if (!endpoint) return;
    const csrfToken = readCsrfTokenFromCookie();
    if (!csrfToken) return;
    await fetch(endpoint, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ theme_mode: mode }),
    });
  }

  function bindThemeTogglePersistence() {
    const toggles = document.querySelectorAll(".theme-toggle");
    if (!toggles.length) return;

    toggles.forEach((toggle) => {
      toggle.addEventListener("click", function () {
        window.setTimeout(function () {
          const mode = readCurrentThemeMode();
          void persistThemeMode(mode);
        }, 0);
      });
    });
  }

  function bootstrapThemeFromBackend() {
    const mode = normalizeThemeMode(window.finhubThemePreferenceMode || "light");
    try {
      window.localStorage.setItem("theme", mode);
    } catch (error) {
      // localStorage is optional for this flow.
    }
    document.documentElement.dataset.theme = mode;
  }

  document.addEventListener("DOMContentLoaded", function () {
    bootstrapThemeFromBackend();
    bindThemeTogglePersistence();
  });
})();
