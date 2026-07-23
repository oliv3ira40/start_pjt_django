# Política de testes

## Objetivo

Definir uma prática de testes para mudanças relevantes, priorizando segurança, isolamento de dados, persistência correta e prevenção de regressões.

## Regra operacional

Toda funcionalidade relevante e toda correção de bug relevante devem receber testes automatizados compatíveis com o comportamento alterado. Quando tecnicamente viável, o teste de regressão deve falhar antes da correção e passar depois dela.

Isso é obrigatório para mudanças em:

- regras de domínio e persistência;
- autorização, permissão, ownership e privacidade;
- querysets, filtros, formulários e relacionamentos;
- endpoints que modificam estado;
- fluxos administrativos ou públicos críticos;
- jobs, seeds, integrações e operações idempotentes.

## Segurança e isolamento de dados

Em fluxos multi-tenant ou com dados pessoais, a cobertura de isolamento é obrigatória:

- usuário comum vê somente os dados permitidos pelo seu escopo;
- superusuário tem visão global somente quando o produto a prevê;
- acesso, edição e exclusão por URL direta de objeto alheio são bloqueados sem vazamento;
- querysets, ações em massa, formulários e relações FK/M2M respeitam o escopo no backend;
- alteração de permissões produz efeito na próxima requisição;
- uma conta não altera, exclui ou infere dados de outra.

Não remova, enfraqueça ou altere testes de segurança por conveniência sem autorização explícita. Mudanças nesse tipo de regra devem preservar ou fortalecer a cobertura.

## Critérios mínimos por mudança

### Regra de negócio ou persistência

- Caminho feliz.
- Validação ou erro relevante.
- Persistência correta no banco e ausência de duplicação quando aplicável.

### Endpoint ou fluxo de interface crítico

- Método, autenticação, CSRF e autorização.
- Dados de entrada válidos e inválidos.
- Resposta e efeito persistido, não apenas mensagem visual.

### Integração e operações assíncronas

- Falha externa não corrompe o estado local.
- Retentativas são idempotentes.
- Efeitos externos ocorrem após a confirmação da transação local.

## Estratégia incremental

Não é obrigatório criar cobertura retroativa total do legado. Ao tocar um fluxo relevante, inclua ou ajuste os testes do escopo no mesmo ciclo. Gaps em áreas sensíveis devem ser registrados e priorizados gradualmente.

Testes visuais, snapshots de HTML/CSS e inspeção manual não substituem testes de regra de negócio, segurança e isolamento.

## Checklist de entrega

- Há testes para o comportamento novo ou corrigido.
- Há cobertura de isolamento quando existem dados por usuário.
- A suíte afetada foi executada localmente.
- `python manage.py check` foi executado quando aplicável.
- Migrations e documentação foram atualizadas quando o contrato mudou.

## Comandos de referência

```bash
python manage.py test
python manage.py check
python manage.py makemigrations --check
```
