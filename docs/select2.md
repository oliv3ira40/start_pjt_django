# Select2 no Django Admin

## Estratégia de inicialização
O arquivo `apiary/js/hive_species_filter.js` é carregado pelo `Select2AdminMixin` logo após o CDN oficial do Select2. Ele verifica se `$.fn.select2` está disponível e, em seguida, executa `initializeSpeciesFilter` após `DOMContentLoaded` (ou imediatamente, caso o DOM já esteja pronto). A função aguarda 200 ms antes de aplicar o plugin para evitar conflitos com widgets ainda em renderização.【F:apiary/admin.py†L28-L41】【F:apiary/static/apiary/js/hive_species_filter.js†L1-L35】

## Seletores padrão e opt-in
O script inicial cobre explicitamente os seguintes elementos:
- Dropdown de filtro lateral (`.list-filter-dropdown select`).
- Campos `#id_species`, `#id_hive`, `#id_city`, `#id_origin_hive` e `#id_box_model` presentes nos formulários de colmeias e revisões.【F:apiary/static/apiary/js/hive_species_filter.js†L8-L27】

Não há mecanismo genérico de `data-select2` no código atual; para adicionar novos selects basta estender o arquivo e incluir um seletor específico ou criar um `data-attribute` customizado antes de chamar `.select2()`.

## Reaplicação em inlines e integração com condicionais
O script padrão não intercepta eventos `formset:added`. Em formulários inline que adicionam selects dinamicamente, é necessário chamar manualmente `$(row).find('select').select2()` dentro do handler ou duplicar a lógica de `initializeSpeciesFilter`. Como o plugin convive com os campos condicionais (que apenas ocultam containers) e com a prévia de imagem (que atua em `input[type="file"]`), não há conflitos diretos; apenas assegure que o seletor utilizado permaneça visível quando a regra estiver ativa.

## Boas práticas
- **Evite dupla inicialização:** sempre teste `if (!element.data('select2'))` antes de chamar `.select2()` em blocos personalizados para prevenir warnings do plugin.  
- **Carregamento assíncrono:** mantenha o CDN ou forneça um build local equivalente. Sem o arquivo `select2.full.min.js`, o script retorna imediatamente e nenhum select será aprimorado.【F:apiary/static/apiary/js/hive_species_filter.js†L2-L4】  
- **Perfomance:** limite os seletores a campos relevantes; aplicar Select2 a milhares de opções pode exigir configurações adicionais (paginação remota, por exemplo).

## Troubleshooting
- **Select2 não aparece:** confirme o carregamento do CDN (inspecione a aba Network) e verifique se o seletor alvo realmente existe quando `initializeSpeciesFilter` roda.【F:apiary/static/apiary/js/hive_species_filter.js†L6-L35】  
- **Erro `select2 is not a function`:** normalmente indica que o CDN falhou ou o jQuery usado não é o mesmo do Django (`django.jQuery`). O script já busca `django.jQuery` por padrão; evite substituir essa referência.  
- **Campos adicionados dinamicamente sem Select2:** replique a chamada `.select2()` após adicionar a linha inline ou extraia `initializeSpeciesFilter` para reutilização nos eventos `formset:added`.  
- **Visual quebrado:** verifique se o CSS do CDN foi carregado e se `apiary/css/image-preview.css` não foi removido da pilha de mídia — ele acompanha o Select2 para manter consistência visual no Admin.【F:apiary/admin.py†L30-L41】
