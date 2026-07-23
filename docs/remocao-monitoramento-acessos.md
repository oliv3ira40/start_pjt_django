# Remoção de monitoramento interno de acessos

## Resumo

O projeto não possui monitoramento interno de acessos por middleware, dashboard administrativo ou coleta própria de eventos. Essa ausência é intencional.

## Diretriz

- Não reintroduza coleta de eventos de acesso, painéis de monitoramento ou rastreamento interno por inferência.
- Qualquer proposta de observabilidade deve ser isolada, ter finalidade definida, passar por avaliação de privacidade e receber aprovação explícita.
- Logs técnicos necessários devem evitar dados pessoais e segredos, seguir retenção proporcional e permanecer protegidos contra acesso indevido.

## Dados legados

Se existirem tabelas ou registros de uma solução anterior, a remoção física deve ocorrer somente em migration planejada, revisada e aprovada. A base de código não deve depender desses dados.
