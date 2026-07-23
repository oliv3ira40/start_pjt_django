(() => {
  const fields = [...document.querySelectorAll('[data-select-mode]')];
  const closeAll = (except) => fields.forEach((field) => { if (field !== except) close(field); });
  const isMultiple = (field) => field.dataset.selectMode.startsWith('multiple');
  const isAjax = (field) => field.dataset.selectMode.endsWith('ajax');
  const selected = (select) => [...select.options].filter((option) => option.selected && option.value);
  const dispatch = (select) => ['input','change'].forEach((type) => select.dispatchEvent(new Event(type, {bubbles:true})));
  const close = (field) => { field.querySelector('.select-dropdown').hidden = true; field.querySelector('.select-trigger').setAttribute('aria-expanded','false'); };
  const choices = (field, query = '') => {
    if (!isAjax(field)) return [...field.querySelector('select').options].filter((option) => option.value).map((option) => ({id:option.value,name:option.text}));
    return (field.dataset.searchItems || '').split(';').map((item, index) => { const [name, secondary] = item.split('|'); return {id:String(index + 1),name,secondary}; }).filter((item) => item.name.toLowerCase().includes(query.toLowerCase()));
  };
  const update = (field) => {
    const select = field.querySelector('select'); const values = selected(select); const triggerValue = field.querySelector('.select-trigger span');
    triggerValue.textContent = values.length ? (isMultiple(field) ? `${values.length} selecionada${values.length === 1 ? '' : 's'}` : values[0].text) : (isAjax(field) ? 'Busque uma opção' : 'Selecione uma opção');
  };
  const render = (field, query = '') => {
    const select = field.querySelector('select'); const list = field.querySelector('ul'); list.replaceChildren();
    choices(field, query).forEach((item) => {
      const option = [...select.options].find((entry) => entry.value === item.id);
      const button = document.createElement('button'); button.type = 'button'; button.className = 'select-option'; button.setAttribute('role','option'); button.setAttribute('aria-selected', String(Boolean(option?.selected))); button.textContent = item.name;
      if (item.secondary) { const detail = document.createElement('small'); detail.textContent = item.secondary; button.append(detail); }
      button.addEventListener('click', () => { let target = option; if (!target) { target = new Option(item.name, item.id); select.add(target); } if (isMultiple(field)) target.selected = !target.selected; else { [...select.options].forEach((entry) => entry.selected = false); target.selected = true; } dispatch(select); update(field); render(field, query); if (!isMultiple(field)) close(field); }); list.append(button);
    });
  };
  fields.forEach((field) => {
    const trigger = field.querySelector('.select-trigger'); const dropdown = field.querySelector('.select-dropdown'); const search = dropdown.querySelector('input'); const done = dropdown.querySelector('.done');
    field.classList.add('is-initialized'); update(field); render(field);
    trigger.addEventListener('click', () => { const opening = dropdown.hidden; closeAll(field); dropdown.hidden = !opening; trigger.setAttribute('aria-expanded', String(opening)); if (opening) { render(field, search?.value || ''); search?.focus(); } });
    search?.addEventListener('input', () => render(field, search.value)); done?.addEventListener('click', () => close(field));
  });
  document.addEventListener('click', (event) => fields.forEach((field) => { if (!field.contains(event.target)) close(field); }));
})();
