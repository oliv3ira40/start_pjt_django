(function () {
  function byNameSuffix(suffix) {
    return document.querySelector(`[name$="${suffix}"]`);
  }

  function findFormRow(fieldName) {
    const field = document.getElementById(`id_${fieldName}`) || byNameSuffix(fieldName);
    if (!field) return null;
    return field.closest('.form-row') || field.closest('.fieldBox') || field.closest('.form-group');
  }

  function toggleField(fieldName, visible) {
    const row = findFormRow(fieldName);
    if (!row) return;
    row.style.display = visible ? '' : 'none';
    row.setAttribute('aria-hidden', visible ? 'false' : 'true');
  }

  function setRequired(fieldName, required) {
    const input = document.getElementById(`id_${fieldName}`) || byNameSuffix(fieldName);
    if (!input) return;
    if (required) input.setAttribute('required', 'required');
    else input.removeAttribute('required');
  }

  function selectedGoalType() {
    const checked = document.querySelector('input[name$="goal_type"]:checked');
    return checked ? `${checked.value || ''}`.trim() : '';
  }

  function isRecurringChecked() {
    const input = document.getElementById('id_is_recurring') || byNameSuffix('is_recurring');
    return Boolean(input && input.checked);
  }

  function applyRules() {
    const goalType = selectedGoalType();
    const isProvision = goalType === 'provisao';
    const isRecurring = isProvision && isRecurringChecked();

    toggleField('is_recurring', isProvision);
    toggleField('monthly_contribution_capacity', goalType === 'meta');
    toggleField('recurrence_frequency', isRecurring);
    toggleField('default_due_day', isProvision);

    if (!isProvision) {
      const recurringInput = document.getElementById('id_is_recurring') || byNameSuffix('is_recurring');
      if (recurringInput) recurringInput.checked = false;
    }
    setRequired('recurrence_frequency', isRecurring);
    setRequired('target_date', isProvision);
  }

  function ensureGoalTypeHelpNode() {
    const goalTypeField = document.querySelector('input[name$="goal_type"]');
    if (!goalTypeField) return null;
    const container =
      goalTypeField.closest('.form-row') ||
      goalTypeField.closest('.fieldBox') ||
      goalTypeField.closest('.form-group');
    if (!container) return null;
    let helper = container.querySelector('[data-goal-type-helper]');
    if (!helper) {
      helper = document.createElement('p');
      helper.className = 'help';
      helper.setAttribute('data-goal-type-helper', '1');
      container.appendChild(helper);
    }
    return helper;
  }

  function updateGoalTypeHelper() {
    const helper = ensureGoalTypeHelpNode();
    if (!helper) return;
    const goalType = selectedGoalType();
    if (goalType === 'provisao') {
      helper.textContent =
        'Ideal para se preparar para gastos previstos e evitar surpresas no orçamento, como IPVA, Natal, aniversários, Dia das Mães, seguros ou despesas sazonais.';
      return;
    }
    helper.textContent =
      'Ideal para objetivos financeiros que você quer alcançar, como uma viagem, uma reserva, uma reforma ou a compra de um item de maior valor.';
  }

  function bind() {
    const goalTypeInputs = Array.from(document.querySelectorAll('input[name$="goal_type"]'));
    const recurringInput = document.getElementById('id_is_recurring') || byNameSuffix('is_recurring');
    goalTypeInputs.forEach((input) => {
      input.addEventListener('change', () => {
        applyRules();
        updateGoalTypeHelper();
      });
    });
    if (recurringInput) {
      recurringInput.addEventListener('change', () => {
        applyRules();
        updateGoalTypeHelper();
      });
    }
    applyRules();
    updateGoalTypeHelper();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
