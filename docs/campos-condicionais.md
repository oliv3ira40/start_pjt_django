# Campos condicionais no Django Admin

O módulo `apiary/js/conditional-fields.js` permite declarar regras em JavaScript puro para mostrar, ocultar ou ajustar o estado de campos do Django Admin sem alterar templates. As regras funcionam em qualquer `ModelAdmin`, inclusive com formulários inline, e respeitam o tema `django-admin-interface`.

## Como registrar regras

1. Garanta que o `BaseAdmin`/`BaseInline` esteja em uso. O mixin `Select2AdminMixin` carrega `apiary/js/conditional-fields.js` automaticamente.
2. Em cada tela que precisa de lógica condicional, defina `window.ADMIN_FIELD_RULES` **até** o carregamento do `DOMContentLoaded` (um bloco `<script>` na página já é suficiente):

```html
<script>
  window.ADMIN_FIELD_RULES = [
    {
      when: { name: "status", is: "publicado" },
      then: [
        { name: "data_publicacao", show: true, set_required: true, clear_on_hide: true },
        { name: "resumo", show: true, set_required: true },
      ],
    },
  ];
</script>
```

As regras são avaliadas na carga da página, a cada mudança dos campos controladores e sempre que inlines são adicionados ou removidos.

## Estrutura das regras (RULES)

Cada entrada aceita os seguintes atributos:

- `when`: objeto ou lista de condições. Campos são identificados pelo **sufixo** do atributo `name`. Operadores disponíveis:
  - `is`: compara o valor atual com uma string específica.
  - `in`: aceita lista/array de valores e passa quando qualquer um for selecionado.
  - `not_in`: oculta/nega quando o valor atual estiver na lista informada.
  - `truthy` / `falsy`: avalia checkbox, radios ou textos vazios.
- `then`: lista de ações aplicadas aos campos alvo (também por sufixo do `name`). Cada ação pode combinar:
  - `show` / `hide`: alterna visibilidade do container do campo.
  - `set_required` / `unset_required`: aplica ou remove `required` e `aria-required`.
  - `enable` / `disable`: controla o atributo `disabled` (respeitando estados padrão).
  - `clear_on_hide`: limpa o campo quando o resultado final for oculto. Funciona junto de `show` ou `hide`.

Se múltiplas regras afetarem o mesmo campo, os efeitos são combinados na ordem declarada. Quando JavaScript não estiver disponível, todos os campos permanecem visíveis e a validação do backend continua obrigatória.

## Exemplos comuns

```javascript
window.ADMIN_FIELD_RULES = [
  // Mostra campos de publicação somente quando o status for "publicado".
  {
    when: { name: "status", is: "publicado" },
    then: [
      { name: "data_publicacao", show: true, set_required: true, clear_on_hide: true },
      { name: "resumo", show: true, set_required: true },
    ],
  },
  // Habilita o campo "observacoes" apenas quando o checkbox for marcado.
  {
    when: { name: "possui_observacoes", truthy: true },
    then: [{ name: "observacoes", enable: true }],
  },
  // Esconde campos de pagamento quando o tipo não exige cobrança.
  {
    when: { name: "tipo", not_in: ["gratuito", "interno"] },
    then: [
      { name: "valor", show: true, set_required: true },
      { name: "codigo_barras", show: true },
    ],
  },
];
```

Os sufixos devem coincidir com o final do atributo `name` dos inputs gerados pelo Django (ex.: `form-0-status` → sufixo `status`). Para atingir elementos específicos em inlines, basta usar o mesmo sufixo; o script calcula automaticamente o prefixo (`form-0-`, `form-1-`, etc.).

## Inlines e eventos dinâmicos

- Novos formulários adicionados via `add another` disparam `formset:added`; o script registra ouvintes nos campos relevantes imediatamente.
- Campos removidos com `formset:removed` são reavaliados para liberar estados aplicados anteriormente.
- Ao exibir novamente um campo oculto, o script emite o evento `admin:conditional:show`, permitindo que outros recursos (por exemplo, Select2) recalcularem a largura/posicionamento.

## Validação e acessibilidade

- A lógica é client-side, mas **não substitui** validações no backend. Mesmo que um campo seja oculto ou desabilitado, a regra de negócio deve ser checada no servidor.
- Containers ocultos recebem `aria-hidden="true"` e têm o foco removido quando necessário, garantindo navegação consistente por teclado e leitores de tela.
- Campos `required` atualizam `aria-required`, mantendo feedback apropriado para usuários assistivos.

Ao combinar as regras com validação server-side, é possível oferecer formulários mais guias sem comprometer a integridade dos dados.
