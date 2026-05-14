# Remoção do monitoramento interno de acessos

Data: 2026-05-14

## Resumo

O monitoramento interno de acessos baseado no app `syshealth` foi removido completamente da base de código.

## O que foi removido

- App `syshealth` e seus módulos (models, admin, views, middleware, forms, metrics, testes e comandos de management).
- Rotas e endpoints de dashboard de acessos no admin customizado.
- Middleware de registro de eventos de acesso.
- Templates do admin vinculados ao painel de saúde/acessos.
- Registro do app em `INSTALLED_APPS`.

## Impacto esperado

- O sistema continua funcionando sem monitoramento interno de acessos.
- Não foi introduzido monitoramento substituto nesta etapa.
- Regras de autenticação, permissões e ownership fora do escopo não foram alteradas.

## Observação sobre dados antigos

Se existirem tabelas/dados legados no banco referentes ao `syshealth`, a remoção física no banco deve ser feita depois, por migração planejada e aprovada.
