# Projeto base Django

Base reutilizável para novos sistemas Django. O projeto prioriza convenções nativas do framework, administração customizável, segurança no backend, isolamento de dados quando aplicável e documentação próxima da implementação.

## Ambiente local

```bash
# Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis locais em .env e aplicar o banco
python manage.py migrate

# Iniciar o servidor
python manage.py runserver

# Criar um superusuário local, se necessário
python manage.py createsuperuser
```

O `direnv` ativa automaticamente a `venv` quando ela existe e o `.envrc` foi autorizado.

## Comandos de verificação

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check
python manage.py collectstatic --noinput
```

Para gerar uma nova chave secreta local:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Nunca versione o arquivo `.env`, chaves, tokens ou credenciais.

## Administração

O projeto utiliza [django-admin-interface](https://github.com/fabiocaccamo/django-admin-interface) como base visual do Django Admin. Superusuários usam o Admin padrão; usuários comuns podem receber menus específicos por escopo quando essa configuração for habilitada.

Itens de menu podem apontar para models ou URLs nomeadas. A navegação não substitui permissões, ownership ou validações no backend.

## Documentação

- [Guia definitivo para agentes](AGENTS.md)
- [Contexto geral do projeto](docs/contexto_do_sistema.txt)
- [Padrões de desenvolvimento](docs/padroes.md)
- [Política de testes](docs/qualidade/politica-de-testes.md)
- [Proteção de dados e exclusão de conta](docs/privacidade/protecao-de-dados-e-exclusao-de-conta.md)
- [Boot compartilhado do Admin](docs/admin_boot.md)
- [Campos condicionais](docs/campos-condicionais.md)
- [Prévia de imagem](docs/preview-image.md)
- [Select2 no Admin](docs/select2.md)
- [Base de onboarding com Driver.js](docs/onboarding/driverjs-base.md)
- [Remoção de monitoramento interno](docs/remocao-monitoramento-acessos.md)
- [Convenções para seeds](docs/seeds/)

Antes de alterar o projeto, leia o `AGENTS.md` e a documentação técnica relacionada à área afetada.
