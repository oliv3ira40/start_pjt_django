# Boot global do Django Admin

## Visão geral
O app `apiary` inicializa comportamentos de Select2, campos condicionais e prévia de imagens para todas as telas do Django Admin através do mixin `Select2AdminMixin`. Esse mixin concentra a declaração de mídia (CSS/JS) e é estendido por `BaseAdmin` e `BaseInline`, garantindo que qualquer `ModelAdmin` ou inline herdando dessas classes carregue automaticamente os recursos compartilhados.【F:apiary/admin.py†L28-L54】

## Arquivos injetados (ordem exata)
1. `https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css`
2. `apiary/css/image-preview.css`
3. `https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.full.min.js`
4. `apiary/js/hive_species_filter.js`
5. `apiary/js/conditional-fields.js`
6. `apiary/js/image-preview.js`

A ordem acima segue o bloco `Media` do `Select2AdminMixin`, garantindo que a folha de estilo local seja carregada após o CSS do Select2 e que o CDN seja inicializado antes dos scripts que o utilizam.【F:apiary/admin.py†L28-L41】

## Como herdar em novos Admin/Inline
- `BaseAdmin` combina `Select2AdminMixin` com `admin.ModelAdmin`. Qualquer classe que estenda `BaseAdmin` recebe automaticamente os assets globais e pode sobrepor configurações padrão se necessário.【F:apiary/admin.py†L44-L47】  
- `OwnerRestrictedAdmin` estende `BaseAdmin` para aplicar filtros de proprietário e é usado por admins que precisam restringir dados por usuário.【F:apiary/admin.py†L56-L104】  
- `BaseInline` é um `admin.TabularInline` pronto para reutilização; embora não injete mídia própria, herdar dele garante consistência e evita duplicação futura. Inlines customizados podem adicionar mídia extra declarando um `class Media` próprio.【F:apiary/admin.py†L50-L53】

Exemplos atuais:
- `SpeciesAdmin`, `BoxModelAdmin`, `CityAdmin`, `SeasonAdmin`, `MellitophilousPlantAdmin`, `RevisionAdmin` e `RevisionAttachmentAdmin` herdam diretamente de `BaseAdmin` para compartilhar os recursos JS/CSS.【F:apiary/admin.py†L106-L403】
- `ApiaryAdmin`, `ColmeiaAdmin`, `QuickObservationAdmin` e `CreatorNetworkEntryAdmin` herdam de `OwnerRestrictedAdmin`, recebendo o mesmo boot global mais as regras de proprietário.【F:apiary/admin.py†L225-L370】
- Inlines como `RevisionAttachmentInline`, `QuickObservationAttachmentInline` e `PlantAttachmentInline` usam `BaseInline`, permitindo que o JavaScript trate eventos como `formset:added` de maneira consistente.【F:apiary/admin.py†L235-L244】【F:flora/admin.py†L17-L27】

## Trecho de referência (`Media`)
```python
class Select2AdminMixin:
    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
                "apiary/css/image-preview.css",
            )
        }
        js = (
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.full.min.js",
            "apiary/js/hive_species_filter.js",
            "apiary/js/conditional-fields.js",
            "apiary/js/image-preview.js",
        )
```
【F:apiary/admin.py†L28-L41】

## Como adicionar um novo app/modelo
1. **Importe** `BaseAdmin` (ou `OwnerRestrictedAdmin`) e `BaseInline` a partir de `apiary.admin`.  
2. **Herde** sua classe de admin de `BaseAdmin` ou `OwnerRestrictedAdmin` para carregar Select2, campos condicionais e prévia de imagem automaticamente.  
3. **Reuse** `BaseInline` para inlines relacionados, adicionando `formfield_for_dbfield` apenas quando precisar marcar inputs (por exemplo, prévia de imagem).  
4. **Opcional:** sobrescreva `class Media` na nova classe somente se precisar incluir assets adicionais — o `Select2AdminMixin.Media` será mantido via herança.  
5. **Teste** o formulário no Admin conferindo se os selects renderizam com Select2, os campos condicionais respondem às mudanças e as prévias de imagem aparecem para inputs marcados.
