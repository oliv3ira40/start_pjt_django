(function () {
  "use strict";

  const rules = [
    {
      when: { name: "yes_no", is: "sim" },
      then: [
        { name: "description", show: true, set_required: true },
      ],
    },
    {
      when: { name: "yes_no", is: "nao" },
      then: [
        { name: "description", hide: true, unset_required: true, clear_on_hide: true },
      ],
    },
  ];

  window.ADMIN_FIELD_RULES = (window.ADMIN_FIELD_RULES || []).concat(rules);
})();
