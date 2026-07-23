# Seed de permissões padrão de grupo

## Objetivo

Definir o padrão para uma seed que cria ou atualiza permissões de um grupo de usuários sem exigir manutenção manual recorrente.

## Comportamento esperado

- Localiza ou cria o grupo por nome normalizado.
- Resolve permissões por `app_label` e `codename`, nunca por IDs numéricos.
- Adiciona somente permissões explicitamente previstas para os models e áreas existentes no projeto.
- Não remove permissões anteriores sem uma migração de política aprovada.
- Registra de forma clara grupo encontrado/criado, permissões adicionadas, já existentes e referências inválidas.

## Segurança e validação

Permissões de grupo não substituem ownership nem autorização contextual. A implementação deve testar primeira execução, reexecução idempotente, referências inválidas e manutenção do isolamento de dados.
