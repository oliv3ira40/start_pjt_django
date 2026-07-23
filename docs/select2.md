# Select2 no Django Admin

## Objetivo

Select2 pode melhorar a seleção de listas extensas no Django Admin, desde que seja aplicado apenas aos campos que se beneficiam de busca, navegação por teclado ou carregamento remoto.

## Inicialização

- Carregue o JavaScript e CSS antes dos scripts que chamam `.select2()`.
- Use `django.jQuery` no Admin para evitar conflitos com outras versões de jQuery.
- Prefira opt-in por `data-select2` ou seletores específicos do componente.
- Antes de inicializar, verifique se o elemento ainda não possui uma instância Select2.
- Em inlines, inicialize somente os selects da linha recebida em `formset:added`.

## Uso responsável

- Limite a inicialização a campos relevantes; listas muito grandes podem exigir autocomplete ou paginação no servidor.
- Filtros e opções disponíveis devem respeitar permissões e ownership no backend.
- O campo HTML original deve continuar submetendo um valor validável pelo formulário Django.
- Se a biblioteca não carregar, o select nativo deve permanecer funcional.

## Troubleshooting

- `select2 is not a function` normalmente indica ordem de carregamento incorreta ou jQuery diferente do usado pelo Admin.
- Se o componente não aparecer, confirme que o seletor existe no momento da inicialização.
- Se um inline não for aprimorado, conecte a inicialização ao evento de formset sem duplicar instâncias existentes.
