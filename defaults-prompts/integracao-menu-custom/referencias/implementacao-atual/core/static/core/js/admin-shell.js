/* Interactive behavior for the administrative shell; menu data remains server-rendered. */
(() => {
  const shell = document.body;
  if (!shell || shell.dataset.adminShellInitialized === "true") return;
  shell.dataset.adminShellInitialized = "true";

  const sidebar = document.querySelector("[data-admin-shell-sidebar]");
  const backdrop = document.querySelector("[data-admin-shell-backdrop]");
  const desktopToggle = document.querySelector("[data-admin-shell-desktop-toggle]");
  const mobileToggle = document.querySelector("[data-admin-shell-mobile-toggle]");
  const mobileClose = document.querySelector("[data-admin-shell-mobile-close]");
  const mobileAccountToggle = document.querySelector("[data-admin-shell-mobile-account-toggle]");
  const mobileAccountMenu = document.querySelector("[data-admin-shell-mobile-account-menu]");
  const search = document.querySelector("[data-admin-shell-search]");
  const tooltip = document.querySelector("[data-admin-shell-tooltip]");
  const desktopQuery = window.matchMedia("(min-width: 821px)");
  if (!sidebar) return;

  const storage = {
    get(key, fallback) {
      try { return window.localStorage.getItem(key) ?? fallback; } catch (_) { return fallback; }
    },
    set(key, value) {
      try { window.localStorage.setItem(key, value); } catch (_) { /* Storage is optional. */ }
    },
  };
  const normalize = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
  const groups = [...sidebar.querySelectorAll("[data-admin-shell-group]")];
  const groupStorageKey = "colmeias-admin-shell-groups";
  const savedGroups = (() => {
    try { return JSON.parse(storage.get(groupStorageKey, "{}")); } catch (_) { return {}; }
  })();
  let scrollY = 0;
  let previousFocus = null;
  let openTimer = 0;
  let closeTimer = 0;
  let groupsBeforeSearch = null;

  const setGroupOpen = (group, open, persist = true) => {
    const trigger = group.querySelector("[data-admin-shell-group-trigger]");
    group.classList.toggle("is-open", open);
    trigger?.setAttribute("aria-expanded", String(open));
    if (persist) {
      savedGroups[group.dataset.adminShellGroupKey] = open;
      storage.set(groupStorageKey, JSON.stringify(savedGroups));
    }
  };
  groups.forEach((group) => {
    const key = group.dataset.adminShellGroupKey;
    if (group.classList.contains("has-active")) setGroupOpen(group, true, false);
    else if (Object.prototype.hasOwnProperty.call(savedGroups, key)) setGroupOpen(group, Boolean(savedGroups[key]), false);
    group.querySelector("[data-admin-shell-group-trigger]")?.addEventListener("click", () => {
      setGroupOpen(group, !group.classList.contains("is-open"));
    });
  });
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => shell.classList.remove("co-admin-shell--initializing"));
  });

  const updateDesktopToggle = () => {
    const collapsed = shell.classList.contains("is-admin-menu-collapsed");
    desktopToggle?.setAttribute("aria-expanded", String(!collapsed));
    desktopToggle?.setAttribute("aria-label", collapsed ? "Expandir menu lateral" : "Minimizar menu lateral");
  };
  const initialCollapsed = storage.get("colmeias-admin-shell-collapsed", "false") === "true";
  shell.classList.toggle("is-admin-menu-collapsed", initialCollapsed);
  updateDesktopToggle();
  desktopToggle?.addEventListener("click", () => {
    shell.classList.remove("is-admin-menu-peek");
    const collapsed = shell.classList.toggle("is-admin-menu-collapsed");
    storage.set("colmeias-admin-shell-collapsed", String(collapsed));
    updateDesktopToggle();
    hideTooltip();
  });

  const canPeek = () => desktopQuery.matches && shell.classList.contains("is-admin-menu-collapsed");
  const openPeek = () => {
    if (!canPeek()) return;
    window.clearTimeout(closeTimer);
    window.clearTimeout(openTimer);
    openTimer = window.setTimeout(() => { shell.classList.add("is-admin-menu-peek"); hideTooltip(); }, 140);
  };
  const closePeek = () => {
    if (!canPeek()) return;
    window.clearTimeout(openTimer);
    window.clearTimeout(closeTimer);
    closeTimer = window.setTimeout(() => {
      if (!sidebar.matches(":hover") && !sidebar.contains(document.activeElement)) shell.classList.remove("is-admin-menu-peek");
    }, 180);
  };
  sidebar.addEventListener("pointerenter", openPeek);
  sidebar.addEventListener("pointerleave", closePeek);
  sidebar.addEventListener("focusin", () => { if (canPeek()) { window.clearTimeout(closeTimer); shell.classList.add("is-admin-menu-peek"); hideTooltip(); } });
  sidebar.addEventListener("focusout", () => window.requestAnimationFrame(() => { if (!sidebar.contains(document.activeElement)) closePeek(); }));

  const hideTooltip = () => {
    if (!tooltip) return;
    tooltip.classList.remove("is-visible");
    document.querySelectorAll('[aria-describedby="co-admin-menu-tooltip"]').forEach((element) => element.removeAttribute("aria-describedby"));
  };
  const showTooltip = (target) => {
    if (!tooltip || !canPeek() || shell.classList.contains("is-admin-menu-peek")) return;
    const label = target.dataset.tooltip || target.textContent.trim();
    if (!label) return;
    tooltip.textContent = label;
    const rect = target.getBoundingClientRect();
    tooltip.style.left = `${rect.right + 10}px`;
    tooltip.style.top = `${Math.max(8, rect.top + (rect.height / 2) - 18)}px`;
    target.setAttribute("aria-describedby", "co-admin-menu-tooltip");
    tooltip.classList.add("is-visible");
  };
  sidebar.addEventListener("pointerover", (event) => { const target = event.target.closest("[data-tooltip]"); if (target) showTooltip(target); });
  sidebar.addEventListener("pointerout", (event) => { if (event.target.closest("[data-tooltip]")) hideTooltip(); });
  sidebar.addEventListener("focusin", (event) => { const target = event.target.closest("[data-tooltip]"); if (target) showTooltip(target); });
  sidebar.addEventListener("focusout", hideTooltip);

  const noResults = document.createElement("p");
  noResults.className = "co-admin-menu-empty";
  noResults.hidden = true;
  noResults.textContent = "Nenhum item encontrado.";
  sidebar.querySelector(".co-admin-sidebar__scroll")?.append(noResults);
  const filterMenu = () => {
    const query = normalize(search?.value.trim() || "");
    const standalone = [...sidebar.querySelectorAll(".co-admin-nav-link")];
    if (!query) {
      standalone.forEach((item) => { item.hidden = false; });
      groups.forEach((group, index) => {
        group.hidden = false;
        if (groupsBeforeSearch) setGroupOpen(group, groupsBeforeSearch[index], false);
        group.querySelectorAll(".co-admin-submenu a").forEach((item) => { item.hidden = false; });
      });
      groupsBeforeSearch = null;
      noResults.hidden = true;
      return;
    }
    if (!groupsBeforeSearch) groupsBeforeSearch = groups.map((group) => group.classList.contains("is-open"));
    let matches = 0;
    standalone.forEach((item) => { const match = normalize(item.textContent).includes(query); item.hidden = !match; if (match) matches += 1; });
    groups.forEach((group) => {
      const groupMatches = normalize(group.querySelector("[data-admin-shell-group-trigger]").textContent).includes(query);
      let childMatches = 0;
      group.querySelectorAll(".co-admin-submenu a").forEach((item) => {
        const match = groupMatches || normalize(item.textContent).includes(query);
        item.hidden = !match;
        if (match) childMatches += 1;
      });
      group.hidden = !(groupMatches || childMatches);
      if (!group.hidden) { matches += 1; setGroupOpen(group, true, false); }
    });
    noResults.hidden = matches > 0;
  };
  search?.addEventListener("input", filterMenu);
  search?.addEventListener("search", filterMenu);

  const closeMobileAccountMenu = () => {
    mobileAccountMenu?.setAttribute("hidden", "");
    mobileAccountToggle?.setAttribute("aria-expanded", "false");
  };
  mobileAccountToggle?.addEventListener("click", (event) => {
    event.stopPropagation();
    const open = mobileAccountMenu?.hidden;
    if (!mobileAccountMenu) return;
    mobileAccountMenu.hidden = !open;
    mobileAccountToggle.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element) || !event.target.closest(".co-admin-mobile-account")) closeMobileAccountMenu();
  });

  const focusableInDrawer = () => [...sidebar.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])')].filter((element) => !element.hidden && element.offsetParent !== null);
  const closeDrawer = () => {
    if (!sidebar.classList.contains("is-mobile-open")) return;
    sidebar.classList.remove("is-mobile-open"); backdrop?.classList.remove("is-mobile-open");
    sidebar.setAttribute("aria-hidden", "true"); backdrop?.setAttribute("aria-hidden", "true");
    mobileToggle?.setAttribute("aria-expanded", "false");
    shell.classList.remove("co-admin-scroll-locked");
    shell.style.position = ""; shell.style.top = ""; shell.style.width = "";
    window.scrollTo(0, scrollY);
    window.setTimeout(() => (previousFocus || mobileToggle)?.focus(), 20);
  };
  const openDrawer = () => {
    if (!window.matchMedia("(max-width: 820px)").matches) return;
    previousFocus = document.activeElement;
    scrollY = window.scrollY;
    shell.style.top = `-${scrollY}px`; shell.style.position = "fixed"; shell.style.width = "100%";
    shell.classList.add("co-admin-scroll-locked");
    sidebar.classList.add("is-mobile-open"); backdrop?.classList.add("is-mobile-open");
    sidebar.setAttribute("aria-hidden", "false"); backdrop?.setAttribute("aria-hidden", "false");
    mobileToggle?.setAttribute("aria-expanded", "true");
    window.setTimeout(() => mobileClose?.focus(), 40);
  };
  mobileToggle?.addEventListener("click", openDrawer);
  mobileClose?.addEventListener("click", closeDrawer);
  backdrop?.addEventListener("click", closeDrawer);
  sidebar.addEventListener("click", (event) => { if (window.matchMedia("(max-width: 820px)").matches && event.target.closest("a[href]")) closeDrawer(); });
  sidebar.addEventListener("keydown", (event) => {
    if (event.key !== "Tab" || !sidebar.classList.contains("is-mobile-open")) return;
    const focusable = focusableInDrawer(); if (!focusable.length) return;
    const first = focusable[0]; const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") { closeDrawer(); closeMobileAccountMenu(); } });
  desktopQuery.addEventListener("change", (event) => { if (event.matches) { closeDrawer(); closeMobileAccountMenu(); } else { shell.classList.remove("is-admin-menu-peek"); hideTooltip(); } });
})();
