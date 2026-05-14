# Diretrizes Atuais do Projeto

## Monitoramento interno de acessos

O recurso interno de monitoramento de acessos (app `syshealth`) foi removido do projeto.

- Não há mais coleta de eventos de acesso via middleware interno.
- Não há mais dashboard/rotas/admin de monitoramento de acessos.
- Não reintroduzir monitoramento por código interno sem decisão explícita do time.

## Banco de dados legado

Caso existam tabelas legadas de monitoramento no banco, elas devem ser tratadas em migração planejada e aprovada separadamente. A base de código atual não depende mais delas.
