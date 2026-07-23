# Integração de menu customizado

Kit de transferência do shell administrativo usado no Colmeias Online.

## Uso

1. Leia `prompt-integracao-menu-custom.txt` e execute os quatro prompts em ordem.
2. Leia o `AGENTS.md` do projeto de destino antes de copiar qualquer componente.
3. Use `referencias/implementacao-atual/` como referência, não como pacote pronto.
4. Adapte fonte de dados, rotas, permissões, tema e identidade ao sistema de destino.
5. A referência inclui os guardrails mobile aprovados: header fixo, logo
   horizontal centralizada, drawer flexível e ações de conta recolhidas e
   ancoradas diretamente sob o botão de perfil.

## Layout aprovado

Coloque aqui o arquivo HTML original ajustado pelo DevFront. Ele é a referência
visual obrigatória, inclusive os paddings e alturas aprovados posteriormente.
Não substitua seus dados demonstrativos pela arquitetura real: o próximo agente
deve adaptar o visual ao menu configurável do sistema de destino.

## Mapa

| Papel | Referência |
| --- | --- |
| Override do Admin | `templates/admin/base_site.html` |
| Cabeçalho | `templates/admin/includes/shell_header.html` |
| Menu | `templates/admin/nav_sidebar.html` |
| Estilos | `core/static/core/css/admin-shell.css` |
| Interações | `core/static/core/js/admin-shell.js` |
| Estado ativo e ícones | `core/templatetags/admin_shell.py` |
| Contexto | `admin_menu/context_processors.py` |
| Fonte de menu e fallback | `admin_menu/sites.py` |
| Seed idempotente de exemplo | `admin_menu/seed_admin_menu.py` |

## Limites

Não há credenciais, banco, identidade visual nem dados do Colmeias neste kit.
Não substitua um menu configurável por `available_apps`; use-o apenas como
fallback se essa já for a arquitetura segura do projeto de destino.
