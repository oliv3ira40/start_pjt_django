# Seed de menu padrão para não-superusuários

## Objetivo

Documentar o padrão de uma seed idempotente para configurar o menu administrativo de usuários não-superusuários.

## Comportamento esperado

- Cria ou localiza o escopo de menu destinado a usuários comuns.
- Cria ou atualiza itens gerenciados pela seed sem duplicar configurações concorrentes.
- Mantém uma ordenação determinística e rótulos coerentes com os apps efetivamente instalados.
- Preserva personalizações que não pertençam à seed, salvo decisão explícita em contrário.
- Usa nomes de rota e referências de model válidos no projeto; não codifica itens de produto que não existam na instalação atual.

## Segurança

A seed configura navegação, não autorização. Permissões, querysets, ownership, relações e bloqueio de URLs diretas continuam obrigatórios no backend.

## Validação

Teste a primeira execução e a reexecução. Ambas devem resultar na mesma configuração, sem itens duplicados e sem ampliar permissões.
