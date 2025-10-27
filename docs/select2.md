# Integração Select2 no Django Admin

O arquivo `apiary/js/hive_species_filter.js` adiciona suporte opcional ao [Select2](https://select2.org/) no Django Admin sem exigir customização de templates. O script só executa quando `$.fn.select2` estiver disponível, garantindo degradação elegante quando o plugin não for carregado.

## Como habilitar

1. Utilize `BaseAdmin`/`BaseInline` para carregar automaticamente o Select2 (via CDN) e o script `apiary/js/hive_species_filter.js`.
2. Opcionalmente, defina `window.SELECT2_START` com uma lista de seletores customizados **antes** do `DOMContentLoaded`. Quando a variável não estiver presente, o fallback cobre `.list-filter-dropdown select`, `#id_species[name="species"]`, `#id_hive`, `#id_city`, `#id_origin_hive` e `#id_box_model`.
3. Aplique o atributo `data-select2="1"` nos `select` que devem ser aprimorados. Esse seletor tem prioridade mesmo quando `window.SELECT2_START` é fornecido.

Além dos campos opt-in, o fallback inicializa automaticamente os filtros do changelist (`.list-filter-dropdown select`).

## Comportamento

- Inicialização única: selects já convertidos não são processados novamente, evitando instâncias duplicadas.
- Respeito a `disabled`/`readonly`: elementos `readonly` são ignorados; selects `disabled` permanecem desabilitados após a conversão.
- Placeholders e `allowClear`: valores definidos via `data-placeholder`, `placeholder` ou `data-allow-clear` são repassados para o Select2.
- Eventos `admin:conditional:show`: quando campos ocultos por regras condicionais são exibidos novamente, o script reajusta a largura do Select2 automaticamente.
- Inlines dinâmicos: eventos `formset:added` aplicam Select2 a novos formulários sem necessidade de código adicional.

## Reexibição condicionada

Quando um campo com Select2 é ocultado e depois mostrado (por exemplo, por `conditional-fields.js`), o evento `admin:conditional:show` faz com que o plugin recalcule a largura do container. Se for necessário acionar manualmente (casos customizados), basta disparar o evento no container do campo:

```javascript
const fieldContainer = document.querySelector('.form-row.field-categoria');
if (fieldContainer) {
  fieldContainer.dispatchEvent(new CustomEvent('admin:conditional:show', { bubbles: true, detail: { container: fieldContainer } }));
}
```

## Inlines e performance

- Os eventos `formset:added` e `formset:removed` são tratados automaticamente. Ao remover um inline, o Select2 correspondente é descartado junto com o DOM do formulário.
- Para telas com muitos selects, prefira limitar o opt-in (`data-select2="1"`) aos campos realmente necessários. Isso mantém a inicialização rápida e reduz o impacto em browsers mais lentos.

## Acessibilidade

O script confia nos recursos de acessibilidade do próprio Select2. Certifique-se de utilizar versões recentes do plugin e de manter os placeholders/mensagens coerentes. Quando o JavaScript não estiver disponível, os `select` continuam funcionando no modo padrão do navegador.
