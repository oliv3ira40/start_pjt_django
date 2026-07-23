(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
    return;
  }
  root.financesPwaInstallUtils = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const FLOW = {
    INSTALLED: "installed",
    NATIVE_PROMPT: "native_prompt",
    IOS_INSTRUCTIONS: "ios_instructions",
    ANDROID_PROMPT_UNAVAILABLE: "android_prompt_unavailable",
    DESKTOP_INFO: "desktop_info",
    UNAVAILABLE: "unavailable",
  };

  const PLATFORM = {
    ANDROID: "android",
    IOS: "ios",
    DESKTOP: "desktop",
    OTHER: "other",
  };

  const BANNER_MODE = {
    HIDDEN: "hidden",
    ANDROID_INSTALL: "android_install",
    IOS_GUIDE: "ios_guide",
  };

  function normalizeUserAgent(value) {
    return `${value || ""}`.trim().toLowerCase();
  }

  function detectPlatform(userAgent) {
    const ua = normalizeUserAgent(userAgent);
    const isIos = /iphone|ipad|ipod/.test(ua) || (ua.includes("macintosh") && ua.includes("mobile"));
    if (isIos) return PLATFORM.IOS;
    if (ua.includes("android")) return PLATFORM.ANDROID;
    const isDesktop = /windows nt|macintosh|x11|linux x86_64|cros/.test(ua);
    if (isDesktop) return PLATFORM.DESKTOP;
    return PLATFORM.OTHER;
  }

  function isMobilePlatform(platform) {
    return platform === PLATFORM.ANDROID || platform === PLATFORM.IOS;
  }

  function resolveInstallFlow(params) {
    const input = params && typeof params === "object" ? params : {};
    const platform = input.platform || PLATFORM.OTHER;
    if (Boolean(input.isStandalone)) return FLOW.INSTALLED;
    if (platform === PLATFORM.IOS) return FLOW.IOS_INSTRUCTIONS;
    if (platform === PLATFORM.ANDROID) {
      if (Boolean(input.hasDeferredPrompt)) return FLOW.NATIVE_PROMPT;
      return FLOW.ANDROID_PROMPT_UNAVAILABLE;
    }
    if (platform === PLATFORM.DESKTOP) return FLOW.DESKTOP_INFO;
    return FLOW.UNAVAILABLE;
  }

  function resolveCtaLabel(params) {
    const input = params && typeof params === "object" ? params : {};
    const flow = input.flow || FLOW.UNAVAILABLE;
    if (flow === FLOW.INSTALLED) return "App instalado";
    if (flow === FLOW.IOS_INSTRUCTIONS) return "Adicionar à tela inicial";
    if (flow === FLOW.NATIVE_PROMPT || flow === FLOW.ANDROID_PROMPT_UNAVAILABLE) return "Instalar app";
    return "";
  }

  function resolveGuideContent(params) {
    const input = params && typeof params === "object" ? params : {};
    const flow = input.flow || FLOW.UNAVAILABLE;
    if (flow === FLOW.IOS_INSTRUCTIONS) {
      return {
        title: "Adicionar à tela inicial",
        description: "No iPhone, use o menu Compartilhar do navegador para adicionar este app à tela inicial.",
        steps: [
          "Toque no botão Compartilhar no Safari.",
          "Selecione Adicionar à Tela de Início.",
          "Confirme para usar o Finances Hub como app.",
        ],
      };
    }
    if (flow === FLOW.ANDROID_PROMPT_UNAVAILABLE) {
      return {
        title: "Instalação automática indisponível",
        description: "Não foi possível abrir o instalador automático neste Android agora.",
        steps: [],
      };
    }
    if (flow === FLOW.DESKTOP_INFO) {
      return {
        title: "Instalação voltada para celular",
        description: "A instalação do app está disponível na experiência mobile.",
        steps: [],
      };
    }
    if (flow === FLOW.UNAVAILABLE) {
      return {
        title: "Instalação indisponível",
        description: "Este navegador/dispositivo não oferece instalação direta do app neste momento.",
        steps: [],
      };
    }
    return {
      title: "Instalar app",
      description: "Siga o fluxo de instalação do seu navegador.",
      steps: [],
    };
  }

  function resolveInstallBannerMode(params) {
    const input = params && typeof params === "object" ? params : {};
    const flow = input.flow || FLOW.UNAVAILABLE;
    const platform = input.platform || PLATFORM.OTHER;
    if (Boolean(input.isStandalone)) return BANNER_MODE.HIDDEN;
    if (Boolean(input.isDismissedByUser)) return BANNER_MODE.HIDDEN;
    if (input.hasPendingInstallRelease === false) return BANNER_MODE.HIDDEN;
    if (
      platform === PLATFORM.ANDROID &&
      flow === FLOW.NATIVE_PROMPT
    ) {
      return BANNER_MODE.ANDROID_INSTALL;
    }
    if (flow === FLOW.IOS_INSTRUCTIONS && platform === PLATFORM.IOS) {
      return BANNER_MODE.IOS_GUIDE;
    }
    return BANNER_MODE.HIDDEN;
  }

  return {
    FLOW,
    PLATFORM,
    BANNER_MODE,
    detectPlatform,
    isMobilePlatform,
    resolveInstallFlow,
    resolveCtaLabel,
    resolveGuideContent,
    resolveInstallBannerMode,
  };
});
