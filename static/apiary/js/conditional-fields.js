/* global window, document */
(function () {
  "use strict";

  const RAW_RULES = window.ADMIN_FIELD_RULES || [];
  const FIELD_CONTAINER_SELECTORS = [
    ".form-row",
    ".form-group",
    ".fieldBox",
    ".field-box",
    ".form-field",
    "div.field",
    "li.form-row",
    "td[class*='field-']",
  ];
  const FIELD_CONTAINER_SELECTOR = FIELD_CONTAINER_SELECTORS.join(", ");

  const controllerSuffixes = new Set();
  const controllerBindings = new Map();
  const baseStateByElement = new WeakMap();
  const containerBaseState = new WeakMap();
  const lastAppliedState = new Map();

  let normalisedRules = [];
  let controllerSelector = "";
  let applyScheduled = false;

  function cssEscape(value) {
    if (typeof value !== "string") {
      return "";
    }
    if (window.CSS && typeof window.CSS.escape === "function") {
      return window.CSS.escape(value);
    }
    return value.replace(/([\0-\x1f\x7f-\x9f\-\[\]{}()*+?.,\\^$|#\s])/g, "\\$1");
  }

  function toArray(value) {
    if (Array.isArray(value)) {
      return value.slice();
    }
    if (value === undefined || value === null) {
      return [];
    }
    return [value];
  }

  function normaliseCondition(source) {
    if (!source || typeof source !== "object") {
      return null;
    }
    const suffix =
      typeof source.name === "string"
        ? source.name
        : typeof source.nameEndsWith === "string"
        ? source.nameEndsWith
        : null;
    if (!suffix) {
      return null;
    }
    return {
      suffix,
      is: source.is,
      in: source.in,
      notIn: source.not_in,
      truthy: source.truthy,
      falsy: source.falsy,
    };
  }

  function normaliseAction(source) {
    if (!source || typeof source !== "object") {
      return null;
    }
    const suffix =
      typeof source.name === "string"
        ? source.name
        : typeof source.nameEndsWith === "string"
        ? source.nameEndsWith
        : null;
    if (!suffix) {
      return null;
    }
    return {
      suffix,
      show: Boolean(source.show),
      hide: Boolean(source.hide),
      setRequired: Boolean(source.set_required),
      unsetRequired: Boolean(source.unset_required),
      enable: Boolean(source.enable),
      disable: Boolean(source.disable),
      clearOnHide: Boolean(source.clear_on_hide),
    };
  }

  function normaliseRule(rule) {
    if (!rule || typeof rule !== "object") {
      return null;
    }
    const whenSource = Array.isArray(rule.when) ? rule.when : [rule.when];
    const thenSource = Array.isArray(rule.then) ? rule.then : [rule.then];

    const conditions = whenSource
      .map(normaliseCondition)
      .filter(Boolean);
    const actions = thenSource
      .map(normaliseAction)
      .filter(Boolean);

    if (!conditions.length || !actions.length) {
      return null;
    }
    return { conditions, actions };
  }

  function normaliseRules(rawRules) {
    return toArray(rawRules)
      .map(normaliseRule)
      .filter(Boolean);
  }

  function computeControllerSelector() {
    if (!controllerSuffixes.size) {
      controllerSelector = "";
      return;
    }
    const parts = [];
    controllerSuffixes.forEach((suffix) => {
      parts.push(`[name$="${cssEscape(suffix)}"]`);
    });
    controllerSelector = parts.join(",");
  }

  function setUpRules() {
    normalisedRules = normaliseRules(RAW_RULES);
    controllerSuffixes.clear();
    normalisedRules.forEach((rule) => {
      rule.conditions.forEach((condition) => {
        controllerSuffixes.add(condition.suffix);
      });
    });
    computeControllerSelector();
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

  function collectElements(root, selector) {
    if (!selector) {
      return [];
    }
    const context = getQueryRoot(root);
    const elements = [];
    if (context.matches && context.matches(selector)) {
      elements.push(context);
    }
    const found = context.querySelectorAll ? context.querySelectorAll(selector) : [];
    for (let index = 0; index < found.length; index += 1) {
      elements.push(found[index]);
    }
    return elements;
  }

  function getNamePrefix(fullName, suffix) {
    if (!fullName || !suffix) {
      return null;
    }
    if (!fullName.endsWith(suffix)) {
      return null;
    }
    return fullName.slice(0, fullName.length - suffix.length);
  }

  function findControllers(condition, root) {
    const selector = `[name$="${cssEscape(condition.suffix)}"]`;
    return collectElements(root || document, selector);
  }

  function findTargets(action, prefix) {
    const selector = `[name$="${cssEscape(action.suffix)}"]`;
    const elements = collectElements(document, selector);
    const matches = [];
    for (let index = 0; index < elements.length; index += 1) {
      const element = elements[index];
      const elementName = element && element.name ? element.name : "";
      if (prefix === null) {
        matches.push(element);
        continue;
      }
      const currentPrefix = getNamePrefix(elementName, action.suffix);
      if (currentPrefix === prefix) {
        matches.push(element);
      }
    }
    return matches;
  }

  function getRadioGroupValues(element) {
    if (!element || !element.name) {
      return [];
    }
    const selector = `input[type="radio"][name="${cssEscape(element.name)}"]:checked`;
    const radios = document.querySelectorAll(selector);
    const values = [];
    for (let index = 0; index < radios.length; index += 1) {
      values.push(radios[index].value);
    }
    return values;
  }

  function getCurrentValues(element) {
    if (!element) {
      return [];
    }
    if (element.type === "radio") {
      return getRadioGroupValues(element);
    }
    if (element.type === "checkbox") {
      return element.checked ? [element.value || "on"] : [];
    }
    if (element.options && element.multiple) {
      const values = [];
      const options = element.options;
      for (let index = 0; index < options.length; index += 1) {
        const option = options[index];
        if (option && option.selected) {
          values.push(option.value);
        }
      }
      return values;
    }
    if (element.value === undefined || element.value === null) {
      return [];
    }
    return [element.value];
  }

  function hasTruthyValue(element, values) {
    if (element && element.type === "checkbox") {
      return Boolean(element.checked);
    }
    if (!values || !values.length) {
      return false;
    }
    for (let index = 0; index < values.length; index += 1) {
      const value = values[index];
      if (value === undefined || value === null) {
        continue;
      }
      const stringValue = String(value).trim();
      if (!stringValue) {
        continue;
      }
      if (stringValue === "0" || stringValue.toLowerCase() === "false") {
        continue;
      }
      return true;
    }
    return false;
  }

  function valuesContain(values, candidate) {
    const target = String(candidate);
    for (let index = 0; index < values.length; index += 1) {
      if (String(values[index]) === target) {
        return true;
      }
    }
    return false;
  }

  function intersects(values, candidates) {
    for (let index = 0; index < candidates.length; index += 1) {
      if (valuesContain(values, candidates[index])) {
        return true;
      }
    }
    return false;
  }

  function evaluateCondition(condition, controller) {
    const values = getCurrentValues(controller);
    if (condition.truthy && !hasTruthyValue(controller, values)) {
      return false;
    }
    if (condition.falsy && hasTruthyValue(controller, values)) {
      return false;
    }
    if (condition.is !== undefined && condition.is !== null) {
      if (!valuesContain(values, condition.is)) {
        return false;
      }
    }
    if (condition.in !== undefined && condition.in !== null) {
      const candidates = toArray(condition.in);
      if (!candidates.length || !intersects(values, candidates)) {
        return false;
      }
    }
    if (condition.notIn !== undefined && condition.notIn !== null) {
      const forbidden = toArray(condition.notIn);
      if (forbidden.length && intersects(values, forbidden)) {
        return false;
      }
    }
    return true;
  }

  function getFieldContainer(element) {
    if (!element) {
      return null;
    }
    if (element.closest && FIELD_CONTAINER_SELECTOR) {
      const found = element.closest(FIELD_CONTAINER_SELECTOR);
      if (found) {
        return found;
      }
    }
    let current = element.parentElement;
    while (current && current !== document) {
      if (current.matches && current.matches(FIELD_CONTAINER_SELECTOR)) {
        return current;
      }
      current = current.parentElement;
    }
    return element.parentElement || null;
  }

  function isElementVisible(element) {
    const container = getFieldContainer(element);
    if (!container) {
      return true;
    }
    if (container.hidden) {
      return false;
    }
    if (container.style && container.style.display === "none") {
      return false;
    }
    if (window.getComputedStyle) {
      const computed = window.getComputedStyle(container);
      if (computed && computed.display === "none" && computed.visibility !== "visible") {
        return false;
      }
    }
    if (typeof container.offsetParent !== "undefined") {
      return container.offsetParent !== null;
    }
    return true;
  }

  function ensureBaseState(element) {
    if (!element) {
      return { required: false, disabled: false, visible: true };
    }
    let base = baseStateByElement.get(element);
    if (!base) {
      base = {
        required: Boolean(element.required),
        disabled: Boolean(element.disabled),
        visible: isElementVisible(element),
      };
      baseStateByElement.set(element, base);
    }
    return base;
  }

  function ensureContainerState(container) {
    if (!container) {
      return { display: "", ariaHidden: null };
    }
    let base = containerBaseState.get(container);
    if (!base) {
      base = {
        display: container.style ? container.style.display || "" : "",
        ariaHidden: container.getAttribute ? container.getAttribute("aria-hidden") : null,
      };
      containerBaseState.set(container, base);
    }
    return base;
  }

  function dispatchVisibilityEvent(container, element, visible) {
    if (!container || typeof window.CustomEvent !== "function") {
      return;
    }
    const eventName = visible ? "admin:conditional:show" : "admin:conditional:hide";
    const event = new window.CustomEvent(eventName, {
      bubbles: true,
      detail: { container, element },
    });
    container.dispatchEvent(event);
  }

  function applyVisibility(element, visible) {
    const container = getFieldContainer(element);
    if (!container) {
      if (visible) {
        element.hidden = false;
      } else {
        element.hidden = true;
      }
      return;
    }
    const base = ensureContainerState(container);
    const wasHidden = container.style.display === "none" || container.hasAttribute("hidden");
    if (visible) {
      if (container.dataset) {
        delete container.dataset.adminConditionalHidden;
      }
      container.style.display = base.display || "";
      if (base.ariaHidden === null || base.ariaHidden === undefined) {
        container.removeAttribute("aria-hidden");
      } else {
        container.setAttribute("aria-hidden", base.ariaHidden);
      }
      container.classList.remove("is-hidden-by-conditional");
      if (wasHidden) {
        dispatchVisibilityEvent(container, element, true);
      }
    } else {
      if (container.contains && container.contains(document.activeElement)) {
        try {
          document.activeElement.blur();
        } catch (error) {
          // ignore
        }
      }
      if (container.dataset) {
        container.dataset.adminConditionalHidden = "1";
      }
      container.style.display = "none";
      container.setAttribute("aria-hidden", "true");
      container.classList.add("is-hidden-by-conditional");
      if (!wasHidden) {
        dispatchVisibilityEvent(container, element, false);
      }
    }
  }

  function applyRequired(element, required) {
    if (!element) {
      return;
    }
    if (required) {
      element.required = true;
      element.setAttribute("required", "required");
      element.setAttribute("aria-required", "true");
    } else {
      element.required = false;
      element.removeAttribute("required");
      element.setAttribute("aria-required", "false");
    }
  }

  function applyDisabled(element, disabled) {
    if (!element) {
      return;
    }
    element.disabled = Boolean(disabled);
    if (disabled) {
      element.setAttribute("disabled", "disabled");
    } else {
      element.removeAttribute("disabled");
    }
  }

  function triggerChange(element) {
    if (!element) {
      return;
    }
    const event = new window.Event("change", { bubbles: true });
    element.dispatchEvent(event);
  }

  function clearValue(element) {
    if (!element) {
      return;
    }
    if (element.type === "checkbox" || element.type === "radio") {
      if (element.type === "radio" && element.name) {
        const selector = `input[type="radio"][name="${cssEscape(element.name)}"]`;
        const radios = document.querySelectorAll(selector);
        for (let index = 0; index < radios.length; index += 1) {
          radios[index].checked = false;
        }
      } else {
        element.checked = false;
      }
      triggerChange(element);
      return;
    }
    if (element.options && element.multiple) {
      for (let index = 0; index < element.options.length; index += 1) {
        element.options[index].selected = false;
      }
      triggerChange(element);
      return;
    }
    if (element.value !== undefined) {
      element.value = "";
      triggerChange(element);
    }
  }

  function evaluateRules() {
    const aggregated = new Map();

    normalisedRules.forEach((rule) => {
      const prefixMap = new Map();
      rule.conditions.forEach((condition, conditionIndex) => {
        const controllers = findControllers(condition);
        controllers.forEach((controller) => {
          if (!controller || !controller.name) {
            return;
          }
          const prefix = getNamePrefix(controller.name, condition.suffix);
          if (prefix === null) {
            return;
          }
          if (!prefixMap.has(prefix)) {
            prefixMap.set(prefix, new Map());
          }
          const conditionByPrefix = prefixMap.get(prefix);
          if (!conditionByPrefix.has(conditionIndex)) {
            conditionByPrefix.set(conditionIndex, controller);
          }
        });
      });

      prefixMap.forEach((controllersByCondition, prefix) => {
        let matches = true;
        rule.conditions.forEach((condition, conditionIndex) => {
          const controller = controllersByCondition.get(conditionIndex);
          if (!controller || !evaluateCondition(condition, controller)) {
            matches = false;
          }
        });

        rule.actions.forEach((action) => {
          const targets = findTargets(action, prefix);
          targets.forEach((target) => {
            if (!aggregated.has(target)) {
              aggregated.set(target, {
                element: target,
                showRules: [],
                hideRules: [],
                setRequiredRules: [],
                unsetRequiredRules: [],
                enableRules: [],
                disableRules: [],
                clearEntries: [],
              });
            }
            const entry = aggregated.get(target);
            if (action.show) {
              entry.showRules.push(matches);
              if (action.clearOnHide) {
                entry.clearEntries.push(!matches);
              }
            }
            if (action.hide) {
              entry.hideRules.push(matches);
              if (action.clearOnHide) {
                entry.clearEntries.push(matches);
              }
            }
            if (action.setRequired) {
              entry.setRequiredRules.push(matches);
            }
            if (action.unsetRequired) {
              entry.unsetRequiredRules.push(matches);
            }
            if (action.enable) {
              entry.enableRules.push(matches);
            }
            if (action.disable) {
              entry.disableRules.push(matches);
            }
          });
        });
      });
    });

    aggregated.forEach((entry) => {
      const element = entry.element;
      const base = ensureBaseState(element);
      let visible = base.visible;
      let required = base.required;
      let disabled = base.disabled;

      if (entry.hideRules.length > 0) {
        if (entry.hideRules.some(Boolean)) {
          visible = false;
        }
      }
      if (entry.showRules.length > 0) {
        visible = entry.showRules.some(Boolean);
      }

      if (entry.unsetRequiredRules.length > 0) {
        if (entry.unsetRequiredRules.some(Boolean)) {
          required = false;
        } else if (entry.setRequiredRules.length === 0) {
          required = base.required;
        }
      }
      if (entry.setRequiredRules.length > 0) {
        required = entry.setRequiredRules.some(Boolean);
      }

      if (entry.enableRules.length > 0) {
        disabled = !entry.enableRules.some(Boolean);
      }
      if (entry.disableRules.length > 0) {
        if (entry.disableRules.some(Boolean)) {
          disabled = true;
        } else if (entry.enableRules.length === 0) {
          disabled = base.disabled;
        }
      }

      const previous = lastAppliedState.get(element) || {
        visible: base.visible,
        required: base.required,
        disabled: base.disabled,
      };

      if (previous.visible !== visible) {
        applyVisibility(element, visible);
      }
      if (previous.required !== required) {
        applyRequired(element, required);
      }
      if (previous.disabled !== disabled) {
        applyDisabled(element, disabled);
      }

      if (!visible && entry.clearEntries.some(Boolean) && previous.visible) {
        clearValue(element);
      }

      lastAppliedState.set(element, { visible, required, disabled });
    });
  }

  function applyRules() {
    applyScheduled = false;
    if (!normalisedRules.length) {
      return;
    }
    evaluateRules();
  }

  function scheduleApply() {
    if (applyScheduled) {
      return;
    }
    applyScheduled = true;
    if (typeof window.requestAnimationFrame === "function") {
      window.requestAnimationFrame(applyRules);
    } else {
      window.setTimeout(applyRules, 0);
    }
  }

  function bindController(element) {
    if (!element || controllerBindings.has(element)) {
      return;
    }
    const handler = function () {
      scheduleApply();
    };
    element.addEventListener("change", handler);
    element.addEventListener("input", handler);
    controllerBindings.set(element, handler);
  }

  function bindControllers(root) {
    if (!controllerSelector) {
      return;
    }
    const elements = collectElements(root || document, controllerSelector);
    elements.forEach(bindController);
  }

  function init() {
    setUpRules();
    if (!normalisedRules.length) {
      return;
    }
    bindControllers(document);
    scheduleApply();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  document.addEventListener("formset:added", function (event) {
    if (!event || !event.target) {
      return;
    }
    bindControllers(event.target);
    scheduleApply();
  });

  document.addEventListener("formset:removed", function () {
    scheduleApply();
  });

  window.addEventListener("load", scheduleApply);
})();
