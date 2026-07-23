# Proteção de dados e exclusão de conta

## Objetivo

Definir um padrão para uma área autenticada de transparência de dados e exclusão definitiva da própria conta. A implementação concreta deve documentar suas rotas, entidades e eventuais obrigações de retenção.

## Experiência esperada

- A área explica, em linguagem simples, quais dados são tratados e para qual finalidade.
- Apresenta um resumo dos dados vinculados à conta que serão removidos.
- Mantém a ação destrutiva visualmente separada das ações rotineiras.
- Não depende apenas de placeholders: informa de forma visível os passos e a irreversibilidade.

## Confirmação robusta

A exclusão deve exigir, no mesmo envio:

- identificação exata da conta autenticada;
- senha atual;
- frase de confirmação inequívoca;
- confirmação explícita de ciência da irreversibilidade.

O endpoint deve aceitar somente `POST`, exigir CSRF, autenticação e validação integral no servidor. Ele não pode receber um alvo externo nem permitir que uma conta exclua dados de outra.

## Comportamento após sucesso

- Remove os dados cujo apagamento é permitido e aplicável ao escopo da conta.
- Encerra sessões autenticadas relevantes.
- Redireciona para uma página pública apropriada, normalmente a de login.
- Não deixa registros parciais ou relações inválidas; use transação quando a operação envolver múltiplas entidades.

## Inventário e retenção

Antes de implementar, mantenha um inventário atualizado das entidades e arquivos ligados à conta. Diferencie claramente dados que serão apagados, anonimizados ou retidos por obrigação legal. Não introduza retenção adicional sem documentação e decisão explícita.

## Testes mínimos

- acesso autenticado à página;
- resumo coerente dos dados do usuário;
- bloqueio de confirmação incompleta;
- bloqueio de tentativa de atingir outra conta;
- exclusão da conta A preservando os dados da conta B;
- encerramento da sessão;
- teste isolado do serviço de exclusão.

Mudanças nesse fluxo exigem regressão de segurança, ownership e privacidade.
