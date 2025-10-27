/* global window, document */
(function () {
  "use strict";

  const INPUT_SELECTOR = 'input[type="file"][data-admin-preview="image"]';
  const PREVIEW_CLASS = "admin-image-preview";
  const IMAGE_CLASS = "admin-image-preview__image";
  const LABEL_CLASS = "admin-image-preview__label";
  const CLEAR_CHECKBOX_SELECTOR =
    'input[type="checkbox"][name$="-clear"], input[type="checkbox"][name$="_clear"]';

  const stateByInput = new Map();

  function cssEscape(value) {
    if (typeof value !== "string") {
      return "";
    }
    if (window.CSS && typeof window.CSS.escape === "function") {
      return window.CSS.escape(value);
    }
    return value.replace(/([\0-\x1f\x7f-\x9f\-\[\]{}()*+?.,\\^$|#\s])/g, "\\$1");
  }

  function getQueryRoot(root) {
    if (!root) {
      return document;
    }
    if (root.querySelectorAll) {
      return root;
    }
    if (root.documentElement) {
      return root.documentElement;
    }
    return document;
  }

  function collectInputs(root, selector) {
    const context = getQueryRoot(root);
    const inputs = [];
    if (context.matches && context.matches(selector)) {
      inputs.push(context);
    }
    const found = context.querySelectorAll ? context.querySelectorAll(selector) : [];
    for (let index = 0; index < found.length; index += 1) {
      inputs.push(found[index]);
    }
    return inputs;
  }

  function findLabelText(input) {
    if (!input) {
      return "Pré-visualização";
    }
    if (input.dataset && input.dataset.adminPreviewLabel) {
      return input.dataset.adminPreviewLabel;
    }
    if (input.id) {
      const label = document.querySelector(`label[for="${cssEscape(input.id)}"]`);
      if (label && label.textContent) {
        return label.textContent.trim();
      }
    }
    return "Pré-visualização";
  }

  function isProbablyImage(url) {
    if (!url || typeof url !== "string") {
      return false;
    }
    const extensionPattern = /\.(gif|ico|jpg|jpeg|png|svg|webp|bmp|tiff?)(\?.*)?$/i;
    return extensionPattern.test(url);
  }

  function detectInitialUrl(input) {
    if (!input) {
      return null;
    }
    const dataset = input.dataset || {};
    const candidates = [
      dataset.adminPreviewInitial,
      dataset.adminPreviewUrl,
      dataset.initialPreviewUrl,
    ];
    for (let index = 0; index < candidates.length; index += 1) {
      const candidate = candidates[index];
      if (candidate) {
        return candidate;
      }
    }
    const wrappers = [
      input.closest && input.closest(".file-upload"),
      input.closest && input.closest(".clearable-file-input"),
      input.parentNode,
    ];
    for (let wrapperIndex = 0; wrapperIndex < wrappers.length; wrapperIndex += 1) {
      const wrapper = wrappers[wrapperIndex];
      if (!wrapper || !wrapper.querySelectorAll) {
        continue;
      }
      const links = wrapper.querySelectorAll("a[href]");
      for (let linkIndex = 0; linkIndex < links.length; linkIndex += 1) {
        const link = links[linkIndex];
        if (link && isProbablyImage(link.getAttribute("href"))) {
          return link.getAttribute("href");
        }
      }
    }
    return null;
  }

  function detectInitialAlt(input, labelText) {
    if (!input) {
      return labelText || "Pré-visualização";
    }
    const dataset = input.dataset || {};
    if (dataset.adminPreviewAlt) {
      return dataset.adminPreviewAlt;
    }
    const wrappers = [
      input.closest && input.closest(".file-upload"),
      input.closest && input.closest(".clearable-file-input"),
      input.parentNode,
    ];
    for (let wrapperIndex = 0; wrapperIndex < wrappers.length; wrapperIndex += 1) {
      const wrapper = wrappers[wrapperIndex];
      if (!wrapper || !wrapper.querySelectorAll) {
        continue;
      }
      const links = wrapper.querySelectorAll("a[href]");
      for (let linkIndex = 0; linkIndex < links.length; linkIndex += 1) {
        const link = links[linkIndex];
        if (link && link.textContent) {
          return link.textContent.trim();
        }
      }
    }
    if (labelText) {
      return `${labelText.trim()} (imagem atual)`;
    }
    return "Imagem atual";
  }

  function ensurePreviewState(input) {
    if (!input || !input.parentNode) {
      return null;
    }
    let state = stateByInput.get(input);
    if (state) {
      return state;
    }

    const figure = document.createElement("figure");
    figure.className = PREVIEW_CLASS;
    figure.hidden = true;

    const image = document.createElement("img");
    image.className = IMAGE_CLASS;
    image.alt = "";
    image.decoding = "async";
    image.style.display = "block";
    image.style.maxWidth = "12rem";
    image.style.maxHeight = "12rem";
    image.style.height = "auto";
    image.style.width = "auto";

    const caption = document.createElement("figcaption");
    caption.className = LABEL_CLASS;
    caption.textContent = findLabelText(input);

    figure.appendChild(image);
    figure.appendChild(caption);

    if (input.nextSibling) {
      input.parentNode.insertBefore(figure, input.nextSibling);
    } else {
      input.parentNode.appendChild(figure);
    }

    state = {
      container: figure,
      image,
      caption,
      initialUrl: null,
      initialAlt: null,
      objectUrl: null,
      bound: false,
    };
    stateByInput.set(input, state);
    return state;
  }

  function revokeObjectUrl(state) {
    if (state && state.objectUrl && window.URL && typeof window.URL.revokeObjectURL === "function") {
      window.URL.revokeObjectURL(state.objectUrl);
      state.objectUrl = null;
    }
  }

  function hidePreview(state) {
    if (!state) {
      return;
    }
    revokeObjectUrl(state);
    state.container.hidden = true;
    state.image.removeAttribute("src");
    state.image.alt = "";
  }

  function showPreview(state, url, altText) {
    if (!state || !url) {
      hidePreview(state);
      return;
    }
    state.image.src = url;
    state.image.alt = altText || state.caption.textContent || "Pré-visualização";
    state.container.hidden = false;
  }

  function updateFromInitial(input, state) {
    if (!state || !input) {
      return;
    }
    state.initialUrl = detectInitialUrl(input);
    state.initialAlt = detectInitialAlt(input, state.caption.textContent);
    if (state.initialUrl) {
      showPreview(state, state.initialUrl, state.initialAlt);
    } else {
      hidePreview(state);
    }
  }

  function updateFromInput(input, state) {
    if (!state || !input) {
      return;
    }
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      revokeObjectUrl(state);
      if (window.URL && typeof window.URL.createObjectURL === "function") {
        const objectUrl = window.URL.createObjectURL(file);
        state.objectUrl = objectUrl;
        showPreview(state, objectUrl, file && file.name ? file.name : state.caption.textContent);
        return;
      }
      if (window.FileReader) {
        const reader = new window.FileReader();
        reader.addEventListener("load", function () {
          showPreview(state, reader.result, file && file.name ? file.name : state.caption.textContent);
        });
        reader.readAsDataURL(file);
        return;
      }
    }
    if (state.initialUrl) {
      showPreview(state, state.initialUrl, state.initialAlt);
    } else {
      hidePreview(state);
    }
  }

  function handleClearChange(input, state, checkbox) {
    if (!checkbox || !input || !state) {
      return;
    }
    if (checkbox.checked) {
      hidePreview(state);
    } else if (!input.files || input.files.length === 0) {
      if (state.initialUrl) {
        showPreview(state, state.initialUrl, state.initialAlt);
      } else {
        hidePreview(state);
      }
    }
  }

  function bindClearCheckboxes(input, state) {
    if (!input || !input.parentNode) {
      return;
    }
    const wrappers = [
      input.closest && input.closest(".clearable-file-input"),
      input.closest && input.closest(".file-upload"),
      input.parentNode,
    ];
    const processed = new Set();
    wrappers.forEach((wrapper) => {
      if (!wrapper || !wrapper.querySelectorAll) {
        return;
      }
      const checkboxes = wrapper.querySelectorAll(CLEAR_CHECKBOX_SELECTOR);
      for (let index = 0; index < checkboxes.length; index += 1) {
        const checkbox = checkboxes[index];
        if (!checkbox || processed.has(checkbox)) {
          continue;
        }
        processed.add(checkbox);
        checkbox.addEventListener("change", function () {
          handleClearChange(input, state, checkbox);
        });
      }
    });
  }

  function bindInput(input) {
    if (!input) {
      return;
    }
    const state = ensurePreviewState(input);
    if (!state || state.bound) {
      return;
    }
    state.bound = true;

    updateFromInitial(input, state);
    bindClearCheckboxes(input, state);

    const refresh = function () {
      updateFromInput(input, state);
    };

    input.addEventListener("change", refresh);
    input.addEventListener("input", refresh);
  }

  function init(root) {
    const inputs = collectInputs(root, INPUT_SELECTOR);
    for (let index = 0; index < inputs.length; index += 1) {
      bindInput(inputs[index]);
    }
  }

  function scheduleInitialisation() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        init(document);
      });
      return;
    }
    init(document);
  }

  scheduleInitialisation();

  document.addEventListener("formset:added", function (event) {
    init(event && event.target ? event.target : document);
  });

  document.addEventListener("formset:removed", function (event) {
    const target = event && event.target ? event.target : null;
    if (!target) {
      return;
    }
    const inputs = collectInputs(target, INPUT_SELECTOR);
    inputs.forEach((input) => {
      const state = stateByInput.get(input);
      if (state) {
        revokeObjectUrl(state);
        stateByInput.delete(input);
      }
    });
  });

  window.addEventListener("beforeunload", function () {
    stateByInput.forEach(function (state) {
      revokeObjectUrl(state);
    });
  });
})();
