# Referência visual dos selects

Abra `layout.html` no navegador para visualizar os quatro componentes: único e
múltiplo locais, único e múltiplo com busca AJAX.

É uma referência de layout e interação, não um pacote pronto para copiar. O
HTML demonstra a arquitetura correta: o campo customizado visível abre um
**dropdown** próprio, enquanto o `<select>` permanece no formulário como fonte
de submissão, valor inicial, fallback sem JavaScript e validação backend.

O exemplo AJAX usa dados locais apenas para a demonstração abrir sem servidor.
Em um projeto real, substitua essa fonte por endpoint de mesma origem, paginado
e autorizado no backend; nunca exponha a relação inteira no HTML.

Não usar esta referência para reintroduzir o select nativo como interface
visível, Select2, CDN ou dependências NPM.
