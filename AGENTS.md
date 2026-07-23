# AGENTS.md — Guia de desenvolvimento Django

Este é o guia definitivo de trabalho do projeto. Ele registra invariantes, padrões reutilizáveis e o método de execução para pessoas e agentes. Documentação de domínio, decisões temporárias e contratos específicos devem ficar em `docs/`, não aqui.

## Hierarquia de decisão e escopo

1. O pedido explícito e as decisões explícitas mais recentes do usuário têm prioridade.
2. Respeite as invariantes deste arquivo e a documentação técnica aplicável.
3. Código, testes e documentação precisam ser analisados juntos; o código existente não comprova que um comportamento é desejado, e testes podem refletir uma implementação incompleta.
4. Quando código ou testes conflitam com um pedido explícito ou uma invariante, corrija-os de forma coerente.
5. Em dúvida, preserve o comportamento atual e peça direcionamento antes de ampliar o escopo.

- Brainstorm, menções conceituais, associação indireta ou contexto lateral não autorizam implementação.
- Implemente somente o que foi solicitado. Não introduza cards, filtros, atalhos, métricas, dependências ou funcionalidades por iniciativa própria.
- Não altere áreas sensíveis — segurança, autenticação, autorização, ownership, privacidade, exclusão de dados, integrações, schema e fluxos públicos — sem solicitação explícita.
- Corrija a causa estrutural, não apenas o sintoma visual. Reutilize implementações equivalentes já existentes; não crie versões paralelas ou divergentes.
- Problemas fora do escopo devem ser relatados ao final como sugestões, sem serem corrigidos por inferência.

## Método de trabalho

- Leia este arquivo integralmente antes de alterar o projeto e consulte a documentação relacionada à área afetada.
- Antes de implementar, audite os consumidores do comportamento: models, forms, admin, views, URLs, templates, JavaScript, serviços, sinais, permissões, testes e documentação quando aplicáveis.
- Prefira mudanças pequenas, isoladas e compatíveis com o comportamento existente.
- Centralize regras compartilhadas em componentes, forms, serviços, validadores, políticas ou helpers. Não duplique lógica por página, modal, endpoint ou camada.
- Use rotas nomeadas e reversão de URLs; não faça URLs hardcoded. Não use parâmetros ou prefixos de URL como mecanismo de autorização.
- Ao concluir, informe de forma objetiva a causa, o impacto, os arquivos alterados e as validações executadas.

## Convenções de código e documentação

- Use `snake_case` para variáveis, campos, módulos, funções e diretórios; `PascalCase` para classes e models.
- Use nomes claros, consistentes com o vocabulário já estabelecido no projeto. Evite abreviações ambíguas e nomes de versões paralelas como `new`, `v2`, `beta` ou `old`.
- Textos de interface devem usar `gettext_lazy` quando aplicável e ser claros, simples e não técnicos para o público final. Defina `verbose_name` e `help_text` úteis em models e forms.
- Validação de domínio é sempre backend-first; máscaras, formatação e validações no cliente são apenas apoio à experiência.
- Documentos e subpastas devem usar nomes em minúsculo. Use o termo `seed` para dados iniciais/demonstração.
- Mantenha documentação próxima do código e atualize o contrato técnico quando uma regra estável mudar. Um arquivo de contexto em `docs/`, quando existir, deve refletir o estado consolidado do projeto.
- Não versione segredos, tokens, credenciais, chaves privadas ou arquivos de ambiente. Não invente, exponha, altere ou publique credenciais de teste.

## Django, dados e migrations

- Respeite os padrões nativos do Django para autenticação, formulários, permissões, Admin, mensagens, CSRF e transações; não altere internals do framework sem necessidade comprovada.
- Não edite nem apague migrations já aplicadas. Mudanças de schema exigem uma nova migration.
- Para mudanças de schema, execute `makemigrations --check`, revise `migrate --plan` quando aplicável e rode `check` e os testes afetados. Em produção, migrations exigem procedimento aprovado e backup quando pertinente.
- Use constraints de banco para invariantes de concorrência e unicidade importantes; validações de aplicação continuam necessárias para mensagens e contexto adequados.
- Operações que modificam vários registros ou dependem de consistência devem usar transações. Efeitos externos devem ocorrer somente após a confirmação da transação local.
- Seeds e comandos de carga devem ser idempotentes: criar ausentes, atualizar o que é gerenciado, manter ordem determinística, não duplicar dados e não apagar personalizações não relacionadas.
- Não execute seeds de demonstração ou alterações operacionais em produção sem autorização explícita e proteção adequada ao ambiente.

## Segurança, privacidade e ownership

- Segurança é requisito transversal. Toda regra crítica de permissão, escopo, integridade e isolamento deve ser validada no servidor.
- Endpoints que alteram estado devem validar método HTTP, autenticação, autorização, CSRF, parâmetros e escopo do usuário. Nunca confie em campos ocultos, filtros visuais, IDs, query strings, relações indiretas, anexos ou JavaScript.
- Em sistemas multi-tenant, usuário comum acessa somente os próprios dados e superusuário mantém a visão global apenas quando isto for intencional.
- Models com `owner` (ou vínculo equivalente) devem aplicar isolamento completo: queryset, criação, edição, exclusão, relações FK/M2M, ações em massa, Admin, views, endpoints e páginas customizadas.
- A criação deve atribuir o proprietário no backend. Usuários comuns não devem escolher nem visualizar campos de ownership sem necessidade explícita.
- O acesso direto por URL a objeto de outro proprietário deve ser bloqueado sem vazar dados. Relações devem oferecer apenas opções do escopo autorizado.
- Menus, botões, redirecionamentos e ocultação visual não substituem autorização no backend. Permissões alteradas devem produzir efeito na próxima requisição.
- Não enfraqueça nem remova testes de segurança, privacidade, permissão, ownership ou visibilidade sem autorização explícita.
- Colete e retenha apenas os dados necessários. Não exponha dados sensíveis em logs, templates, respostas JSON, mensagens de erro, analytics ou ferramentas de terceiros.
- Cookies essenciais de sessão e CSRF devem permanecer funcionais. Qualquer armazenamento opcional, analytics, pixel ou terceiro exige avaliação de privacidade, consentimento quando aplicável e atualização da documentação.
- Tokens, chaves e credenciais de integrações devem vir de variáveis de ambiente, ficar restritos ao backend e nunca aparecer em logs, páginas ou respostas.
- Fluxos destrutivos ou irreversíveis exigem confirmação explícita, validação no servidor, escopo estrito e cobertura de testes.

## Admin, páginas customizadas e UX

- O Django Admin customizado deve preservar consistência entre model, form, campos exibidos, `readonly_fields`, `exclude`, validações e permissões.
- Páginas customizadas devem manter autenticação, autorização e ownership equivalentes às telas administrativas relacionadas. Use URLs nomeadas e `resolver_match.view_name` para estado de menu quando necessário.
- Reutilize componentes e assets oficiais do projeto. CSS e JavaScript de páginas customizadas devem ser isolados para evitar efeitos colaterais globais.
- Quando um layout aprovado for integrado, trate-o como contrato visual: preserve estrutura, hierarquia, estados e comportamentos previstos, conectando-o a dados e fluxos reais. Não copie mocks, persistência simulada ou JavaScript demonstrativo.
- Em layouts próprios dentro do Admin, sobrescreva os blocos de título padrão no template da página quando o layout já possuir título; não esconda títulos globais via CSS ou JavaScript.
- Interfaces devem ser responsivas, acessíveis e objetivas. Priorize linguagem simples, ações inequívocas, feedback de sucesso/erro contextual, toque confortável no mobile e baixa fricção.
- Ações destrutivas devem permanecer distintas de edição e exigir confirmação explícita. Não use `confirm()` quando houver padrão de modal do projeto.
- Não use dados fictícios, estimativas silenciosas ou estados visuais que sugiram persistência sem confirmação real do backend.

## Uploads, integrações e conteúdo público

- Centralize políticas de upload: tipos aceitos, tamanho, dimensões, conversão, nomes internos seguros e remoção após substituição/exclusão confirmada.
- Reutilize validadores e presets de upload; não replique regras em model, form e view. Não aceite arquivos ou formatos não previstos sem decisão explícita.
- Integrações externas devem ficar em serviços de backend centralizados, com timeout, tratamento de falhas, logs seguros e comportamento local consistente quando o serviço externo falhar.
- Chamadas externas devem ser idempotentes e não podem duplicar efeitos em novas tentativas. Não as dispare diretamente de models, templates ou JavaScript.
- Dados e páginas públicas devem ser isolados da área autenticada. Tokens públicos são restritos ao recurso autorizado, longos, aleatórios, revogáveis quando aplicável e nunca substituem ownership.
- Apenas conteúdo público intencional pode ser indexável. Admin, autenticação, áreas privadas, tokens temporários e dados de usuários devem usar `noindex`.
- SEO e metadados devem ser centralizados, reais e baseados em dados permitidos; não use `meta keywords` ou dados estruturados fictícios.

## Qualidade e testes

- Toda implementação relevante e toda correção de bug relevante devem incluir testes automatizados proporcionais ao escopo.
- Escreva testes que reproduzam o cenário e comprovem persistência, resposta, contexto, ordenação, limites, validação, permissões e regressão de consumidores relacionados.
- Uma mensagem de sucesso ou um único registro não comprovam o fluxo: inclua casos múltiplos, limites e cenários negativos quando forem relevantes.
- Sempre que possível, o teste deve falhar antes da correção e passar depois dela.
- Mudanças de ownership, visibilidade, permissões ou rotas exigem testes específicos de isolamento, formulários/relações e bloqueio de acesso direto por URL.
- Mudanças de Admin, model, form ou schema exigem as suítes afetadas e as verificações de migration pertinentes.
- Não marque uma tarefa como concluída sem executar as validações proporcionais ao risco. Declare claramente o que foi executado e o que não pôde ser validado.

## Atualização deste guia

- Atualize este arquivo somente para convenções estruturais, estáveis e reutilizáveis.
- Regras de produto, histórico de decisões, detalhes de implementação e pendências devem ficar em documentação específica.
- Mantenha o guia conciso, organizado e sem duplicações; ao adicionar uma regra, consolide ou remova a versão anterior equivalente.
