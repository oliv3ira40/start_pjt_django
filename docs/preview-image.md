# Prévia de imagem no Admin

## Objetivo e quando usar
O módulo `apiary/js/image-preview.js` adiciona miniaturas automáticas para campos de upload no Django Admin. Ele é indicado para qualquer input de arquivo que armazene imagens e funciona tanto em formulários principais quanto em inlines tabulares.【F:apiary/static/apiary/js/image-preview.js†L1-L398】

## Opt-in
Há duas formas de habilitar a prévia:
- Marcar o campo com `data-image-preview="true"` via `formfield.widget.attrs`. Esse caminho é usado, por exemplo, nos inlines de anexos de plantas.【F:flora/admin.py†L23-L52】
- Deixar que o script aplique automaticamente quando o atributo `name` terminar com `photo` ou `file`, conforme a configuração padrão `FIELDS`.【F:apiary/static/apiary/js/image-preview.js†L5-L18】

Atributos opcionais suportados no dataset: `data-preview-label`, `data-initial-preview-url` e `data-image-preview-thumbnail-class`, todos combinados com as opções declaradas no script.【F:apiary/static/apiary/js/image-preview.js†L147-L188】

## Seletores e eventos
- O script observa inputs `input[type="file"]` marcados com `data-image-preview="true"` ou que atendam às regras de `FIELDS`. A coleta aceita seletores por ID, classe do container, sufixo/prefixo de nome ou seletor CSS arbitrário.【F:apiary/static/apiary/js/image-preview.js†L20-L135】
- Para cada input elegível, é criada uma `<div class="image-preview-wrapper">` contendo um `<img>` com classe `thumb-150`. O container é inserido antes do campo usando `.image-preview-field-container` para preservar a estrutura padrão do Django Admin.【F:apiary/static/apiary/js/image-preview.js†L200-L264】
- Eventos observados: `change` do campo de arquivo, `change` do checkbox de limpeza (`.clearable-file-input`) e `DOMContentLoaded`. O script também responde a `formset:added` para aplicar a prévia em novas linhas de inline.【F:apiary/static/apiary/js/image-preview.js†L281-L398】

## Limites visuais (CSS)
O estilo padrão define miniaturas de até 180×180 px com `object-fit: cover`, espaçamento vertical de 0,35–0,5 rem e tipografia reforçada para o rótulo.【F:apiary/static/apiary/css/image-preview.css†L1-L25】  
Sobrescreva as classes `.thumb-150`, `.image-preview-wrapper` ou `.image-preview-field-container` em um arquivo CSS adicional caso precise de outro tamanho.

## Inlines
Sempre herde de `BaseInline` ou garanta que o script seja carregado junto ao admin. A reinicialização ocorre automaticamente ao escutar `document.addEventListener("formset:added", …)`, portanto inputs adicionados dinamicamente recebem a prévia sem configuração extra.【F:apiary/static/apiary/js/image-preview.js†L388-L397】

## Troubleshooting
- **Prévia não aparece:** confirme que o campo corresponde às regras (`name` termina com `photo`/`file`) ou está marcado com `data-image-preview="true"`. Campos com MIME não suportado não disparam a leitura pelo `FileReader`.  
- **Miniatura não some ao limpar:** verifique se o checkbox “Limpar” está presente; o listener zera o valor do input e remove a imagem quando o checkbox é marcado.【F:apiary/static/apiary/js/image-preview.js†L321-L341】  
- **Imagem antiga continua após upload:** a função `handleChange` substitui a prévia na leitura do novo arquivo e cancela o checkbox de limpeza. Revise se outro script está interferindo com o evento `change`.【F:apiary/static/apiary/js/image-preview.js†L281-L318】  
- **Inline não atualiza:** certifique-se de que o inline herda `BaseInline` (o JS é carregado globalmente) e que não há erro de JavaScript interrompendo o handler `formset:added` antes da execução.【F:apiary/static/apiary/js/image-preview.js†L388-L397】
