# Seed de usuário de demonstração

## Objetivo

Definir o padrão para criar ou reutilizar uma conta local de demonstração com dados sintéticos. A seed permite validar fluxos autenticados, produzir capturas de tela e demonstrar o sistema sem expor dados reais.

## Regras

- As credenciais devem vir de fonte local não versionada; nunca devem ser documentadas no repositório.
- A conta deve ter apenas as permissões necessárias ao cenário de teste e seguir as mesmas regras de ownership de um usuário comum.
- O comando deve recusar execução em produção, salvo autorização explícita e proteção específica para uma finalidade comercial aprovada.
- Dados sintéticos devem ser claramente identificáveis e não conter dados pessoais reais.
- A seed deve ser idempotente: reutiliza a conta e os registros por ela gerenciados, cria somente o que falta e não duplica dados em reexecuções.

## Conteúdo recomendado

Inclua dados variados o bastante para validar listagens, estados vazios, ordenação, filtros, páginas autenticadas e permissões, mas mantenha o conjunto pequeno e previsível.

## Validação

Teste primeira execução, reexecução, normalização de usuário quando aplicável, escopo dos dados criados e bloqueio no ambiente de produção.
