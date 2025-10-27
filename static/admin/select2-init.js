/* global window, document */
(function () {
  "use strict";

  if (!window.jQuery || !window.jQuery.fn || !window.jQuery.fn.select2) {
    return;
  }

  const $ = window.jQuery;
  const FILTER_SELECTOR = ".list-filter-dropdown select";
  const OPT_IN_SELECTOR = 'select[data-select2="1"]';
  const SELECTOR = `${FILTER_SELECTOR}, ${OPT_IN_SELECTOR}`;

  const initialised = new WeakSet();

  function toArray(value) {
    if (Array.isArray(value)) {
      return value.slice();
    }
    if (value === undefined || value === null) {
      return [];
    }
    return [value];
  }

  function ensurePlaceholderOptions($element, options) {
    const dataPlaceholder = $element.attr("data-placeholder") || $element.data("placeholder");
    if (dataPlaceholder !== undefined) {
      options.placeholder = dataPlaceholder;
    }
    const attrPlaceholder = $element.attr("placeholder");
    if (attrPlaceholder) {
      options.placeholder = attrPlaceholder;
    }
    const allowClear = $element.data("allowClear");
    if (allowClear !== undefined) {
      if (typeof allowClear === "boolean") {
        options.allowClear = allowClear;
      } else {
        const allowValues = toArray(allowClear);
        options.allowClear = allowValues.some((item) => String(item) !== "0" && String(item).toLowerCase() !== "false");
      }
    }
    if (options.allowClear && !options.placeholder) {
      options.placeholder = "";
    }
  }

  function initialiseSelect(element) {
    if (!element) {
      return;
    }
    const $element = $(element);
    if ($element.hasClass("select2-hidden-accessible") || $element.data("select2") || initialised.has(element)) {
      return;
    }
    if ($element.prop("readonly")) {
      return;
    }
    const options = { width: "100%" };
    ensurePlaceholderOptions($element, options);
    $element.css("width", "100%");
    $element.select2(options);
    initialised.add(element);
  }

  function refreshSelect(element) {
    if (!element) {
      return;
    }
    const $element = $(element);
    const instance = $element.data("select2");
    if (!instance) {
      return;
    }
    if (instance.$container && instance.$container.length) {
      instance.$container.css("width", "100%");
    }
    $element.trigger("change.select2");
  }

  function collectSelects(root, selector) {
    const elements = [];
    if (!selector) {
      return elements;
    }
    if (root && root.matches && root.matches(selector)) {
      elements.push(root);
    }
    if (root && root.querySelectorAll) {
      const found = root.querySelectorAll(selector);
      for (let index = 0; index < found.length; index += 1) {
        elements.push(found[index]);
      }
    } else if (document.querySelectorAll) {
      const found = document.querySelectorAll(selector);
      for (let index = 0; index < found.length; index += 1) {
        elements.push(found[index]);
      }
    }
    return elements;
  }

  function initialise(root) {
    const selects = collectSelects(root || document, SELECTOR);
    selects.forEach(initialiseSelect);
  }

  function refreshWithin(container) {
    const selects = collectSelects(container, SELECTOR);
    selects.forEach(refreshSelect);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initialise(document);
    });
  } else {
    initialise(document);
  }

  document.addEventListener("formset:added", function (event) {
    if (event && event.target) {
      initialise(event.target);
    }
  });

  document.addEventListener("admin:conditional:show", function (event) {
    if (!event || !event.detail || !event.detail.container) {
      return;
    }
    refreshWithin(event.detail.container);
  });

  document.addEventListener("formset:removed", function () {
    // No action required; select2 cleans up with removed nodes.
  });
})();
