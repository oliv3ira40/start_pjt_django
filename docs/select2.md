# Integração Select2 no Django Admin

O arquivo `static/admin/select2-init.js` adiciona suporte opcional ao [Select2](https://select2.org/) no Django Admin sem exigir customização de templates. O script só executa quando `$.fn.select2` estiver disponível, garantindo degradação elegante quando o plugin não for carregado.

## Como habilitar

1. Assegure-se de copiar o modelo `exemplo-novos-recursos/select2-init.js` para `static/admin/select2-init.js` (veja instruções no [README](../README.md)).
2. Carregue o JavaScript do Select2 e suas dependências (jQuery + CSS) conforme a necessidade do projeto.
3. Inclua `static/admin/select2-init.js` via `ModelAdmin.Media` ou hook global do AdminSite, após importar o Select2.
4. Aplique o atributo `data-select2="1"` nos `select` que devem ser aprimorados.

Além dos campos opt-in, o script inicializa automaticamente selects presentes em filtros do changelist (`.list-filter-dropdown select`).

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
