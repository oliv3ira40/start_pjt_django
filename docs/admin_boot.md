# Boot compartilhado do Django Admin

## Objetivo

Centralizar os assets e os comportamentos reutilizáveis do Django Admin em classes-base ou mixins. Essa organização evita que cada `ModelAdmin` e inline registre manualmente os mesmos CSS, JavaScript e regras de inicialização.

## Estrutura recomendada

- Um mixin de mídia declara os assets compartilhados e sua ordem de carregamento.
- Uma classe-base de `ModelAdmin` reutiliza esse mixin.
- Uma classe-base de inline preserva a mesma convenção e pode acrescentar mídia quando necessário.
- Uma classe restrita por proprietário, quando houver multi-tenancy, estende a classe-base e concentra queryset, atribuição automática de owner e filtros de relações.

## Ordem de carregamento

1. CSS de bibliotecas de terceiros.
2. CSS local que complementa essas bibliotecas.
3. JavaScript das bibliotecas.
4. Scripts locais dependentes das bibliotecas.
5. Scripts independentes, como campos condicionais e prévia de imagem.

Mantenha a ordem documentada no `class Media`. Prefira assets locais ou vendorizados; um CDN só deve ser usado com decisão explícita, integridade adequada e comportamento aceitável em caso de indisponibilidade.

## Uso em novos admins e inlines

1. Herde da classe-base apropriada.
2. Declare mídia adicional somente se ela for exclusiva da tela.
3. Para regras de isolamento, use a classe ou política centralizada; não replique filtros em cada admin.
4. Teste o formulário principal e os inlines dinâmicos, verificando carregamento de assets, acessibilidade e validação no servidor.

## Cuidados

- A camada JavaScript melhora a experiência, mas não substitui formulários e validações Django.
- Scripts que atendem inlines devem reagir a `formset:added` e evitar inicialização duplicada.
- Não transforme um boot global em dependência obrigatória de uma funcionalidade específica de domínio.
