# Selects compartilhados sem Select2

Kit de transferência para criar selects próprios sem dependência de Select2,
CDN, NPM ou picker nativo de iOS.

## Uso

1. Leia integralmente o `AGENTS.md` do projeto de destino.
2. Audite formulários, widgets, Admin, templates, assets e endpoints existentes.
3. Escolha a família pelo volume e pela origem das opções, não pelo nome do campo.
4. Execute o prompt aplicável; execute os dois se o sistema precisar dos quatro
   componentes.
5. Migre consumidores somente depois de os componentes necessários e seus
   testes estarem prontos.

## Prompts

- [Prompt 1 — selects locais](prompts/01-selects-locais.txt): select único e
  múltiplo, sem busca e sem AJAX.
- [Prompt 2 — selects AJAX](prompts/02-selects-ajax.txt): select único e
  múltiplo, com busca remota e endpoint autorizado.

Os dois prompts compartilham regras de integração Django, acessibilidade,
mobile e ausência de Select2. O segundo pressupõe que a base dos selects locais
já tenha sido compreendida ou criada.

## Referência visual

[referencia-visual/layout.html](referencia-visual/layout.html) demonstra, de
forma isolada, o layout e a interação dos quatro componentes, com CSS e
JavaScript próprios. É uma referência de arquitetura: o campo visível é um
botão que abre um dropdown customizado; o `<select>` Django permanece como
controle real de submissão e fallback, mas não é a interface visível depois da
inicialização.

## Os quatro componentes

| Tipo | Busca | Origem das opções | Uso adequado |
| --- | --- | --- | --- |
| Único local | Não | `Select` Django ou queryset pequeno já autorizado | choices estáticos e relações pequenas |
| Múltiplo local | Não | `SelectMultiple` Django ou queryset pequeno já autorizado | poucas opções previamente carregadas |
| Único AJAX | Sim | endpoint próprio, paginado e autorizado | relações grandes ou busca remota |
| Múltiplo AJAX | Sim | endpoint próprio, paginado e autorizado | múltiplas relações grandes |

## Referência de arquitetura validada

No Colmeias Online, os parciais locais são
`templates/admin/includes/local_single_select.html` e
`local_multi_select.html`; os AJAX são `custom_single_select.html` e
`custom_multi_select.html`. Cada família possui CSS e JavaScript próprios.

Esses arquivos são referência de comportamento, não um pacote para copiar sem
auditoria. Projetos de destino devem preservar sua identidade visual, rotas,
formulários, política de ownership e convenções de assets.

## Invariantes

- O controle HTML real continua sendo a fonte de submissão e validação.
- Opções e permissões são definidas no backend; JavaScript apenas apresenta e
  sincroniza o estado.
- Componentes locais não possuem busca nem fazem requisições de rede.
- Componentes AJAX não carregam uma relação inteira no HTML.
- Não usar Select2, `django-select2`, `autocomplete_fields`, CDN ou NPM como
  fallback.
- Assets são carregados somente na página consumidora.
