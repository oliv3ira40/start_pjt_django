# Prévia de imagem no Django Admin

A prévia de imagem permite conferir imediatamente o arquivo selecionado em campos de upload sem recarregar a página do Django Admin. O recurso é totalmente opt-in e funciona em telas de adição, edição e em formulários inline (formsets), mantendo compatibilidade com o tema [`django-admin-interface`](https://github.com/fabiocaccamo/django-admin-interface).

## Como habilitar

1. Garanta que o mixin `Select2AdminMixin` esteja sendo aplicado através de `BaseAdmin`/`BaseInline` (veja a [seção Recursos do Admin](../README.md)). Ele é responsável por carregar `apiary/js/image-preview.js` e `apiary/css/image-preview.css` automaticamente.
2. Nos campos de upload que devem exibir a miniatura, adicione o atributo `data-admin-preview="image"` ao `input[type="file"]`.
3. Opcionalmente informe atributos adicionais no campo:
   - `data-admin-preview-label`: texto exibido na legenda abaixo da miniatura.
   - `data-admin-preview-initial`: URL absoluta da imagem já salva (caso o link padrão do admin não esteja presente ou não seja uma imagem).
   - `data-admin-preview-alt`: texto alternativo customizado para a miniatura.

O script procura automaticamente o link padrão gerado pelo admin (`Currently: <a href="…">`) para exibir a imagem inicial. Se nenhum arquivo for encontrado, a prévia permanece oculta até a seleção de um novo arquivo.

## Comportamento e limites visuais

- A miniatura mantém a proporção original do arquivo e recebe limites de largura/altura máximos (`200px` por padrão) para evitar que imagens grandes quebrem o layout.
- Ao selecionar um novo arquivo, o script usa `URL.createObjectURL` (ou `FileReader` como fallback) para exibir imediatamente a imagem escolhida.
- Se o usuário limpar o campo ou marcar o checkbox “Limpar”, a miniatura volta para o estado inicial ou é ocultada.

Caso precise de tamanhos diferentes, personalize via CSS utilizando as classes utilitárias adicionadas pelo script:

```css
.admin-image-preview {
  max-width: 14rem;
}

.admin-image-preview__image {
  max-width: 100%;
  max-height: 14rem;
}
```

## Inlines dinâmicos

Eventos `formset:added` e `formset:removed` são tratados automaticamente. Novos formulários inline recebem a prévia assim que o `input[type="file"]` com `data-admin-preview="image"` é adicionado, e prévias de formulários removidos têm seus `ObjectURL`s liberados para evitar vazamentos de memória.

## Acessibilidade

- O `alt` da miniatura reutiliza o rótulo associado ao campo ou o valor de `data-admin-preview-alt`.
- A miniatura é marcada como elemento puramente informativo; teclado e navegação por foco continuam funcionando normalmente.
- O script não interfere na validação server-side, portanto campos obrigatórios continuam sendo validados no backend.

## Solução de problemas

| Sintoma | Causa provável | Ação sugerida |
| --- | --- | --- |
| Prévia não aparece | Atributo `data-admin-preview="image"` ausente ou arquivo JS não carregado | Confirme o atributo e a inclusão do script na página |
| Miniatura distorcida | CSS externo sobrescrevendo os limites | Ajuste o CSS do projeto usando as classes `.admin-image-preview` ou `.admin-image-preview__image` |
| Imagem inicial não encontrada | Link padrão não aponta para arquivo de imagem | Forneça a URL inicial via `data-admin-preview-initial` |

A funcionalidade é puramente client-side, portanto, mesmo que o JavaScript falhe, o upload de arquivos continua disponível.
