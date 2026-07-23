# Prévia de imagem no Admin

## Objetivo

A prévia de imagem permite conferir um arquivo selecionado antes do envio, em formulários e inlines do Django Admin. Ela é uma conveniência visual e não substitui a política de upload ou a validação no servidor.

## Ativação

Prefira opt-in explícito com um atributo como `data-image-preview="true"` adicionado pelo widget. Evite habilitação baseada apenas em sufixos genéricos de nome de campo, pois isso pode ativar a prévia em arquivos que não são imagens.

A configuração pode oferecer, quando necessário:

- rótulo de prévia;
- URL da imagem já persistida;
- classe CSS para tamanho ou formato da miniatura.

## Comportamento esperado

- Crie a prévia perto do input, sem quebrar a estrutura do Admin.
- Reaja à seleção de novo arquivo e ao checkbox de limpeza.
- Reaplique o comportamento quando um inline for adicionado dinamicamente.
- Libere URLs temporárias criadas no navegador quando forem substituídas ou removidas.

## Segurança e acessibilidade

- Valide tipo, tamanho, conteúdo e processamento de imagens no backend.
- Não use o nome do arquivo como identificador de armazenamento.
- Informe visualmente quando não houver prévia disponível e forneça texto alternativo adequado.
- Mantenha dimensões controladas com CSS para que imagens grandes não desorganizem o formulário.
