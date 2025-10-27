### Esboço do projeto:

### Comandos úteis

```bash

# Criar a env
$ python3 -m venv venv

# Ativar a env
$ source venv/bin/activate

# Instalar as dependências
$ pip install -r requirements.txt

# Gerar nova secret key
$ python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Colar no arquivo .env

# Desativar a env
$ deactivate

# Criar o banco de dados
$ python manage.py migrate

# Iniciar o projeto
$ python manage.py runserver

# Criar um super usuário
$ python manage.py createsuperuser

# Compilar as mensagens
$ python manage.py compilemessages

# Criar arquivo requirements.txt
$ pip freeze > requirements.txt

# Mandar dependências para o arquivo requirements.txt
$ pip freeze > requirements.txt

# Reiniciar o gunicorn e o nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

```

<!-- django-admin makemessages -l pt_BR -d django -->

### Padrões de desenvolvimento
Clique [aqui](docs/padroes.md) para ver os padrões de desenvolvimento utilizados neste projeto.

### Tema Django utilizado - Django admin interface:
Clique [aqui](https://github.com/fabiocaccamo/django-admin-interface?tab=readme-ov-file) para ver o tema utilizado neste projeto.

### Menu personalizado do Django Admin

Superusuários continuam visualizando o menu padrão do Django. Para usuários comuns é possível definir um menu customizado seguindo os passos abaixo:

1. Acesse o admin com uma conta de superusuário e vá até **Menu do Admin → Configurações de menu**.
2. Crie (ou edite) uma configuração com o escopo **Não superusuários** e marque-a como ativa.
3. Adicione os itens desejados na aba de itens:
   - **Modelo**: informe `app_label` e `model_name` (em minúsculo). O sistema respeita as permissões padrão do admin.
   - **Link personalizado**: informe um `nome da URL` (ex.: `dashboard:index`) ou uma `URL absoluta`. O campo `Permissão extra` aceita o formato `app_label.codename` caso o link exija uma permissão específica.
   - Utilize o campo **Seção** para agrupar itens sob um título customizado (ex.: “Operações”). Quando vazio, o nome do aplicativo é utilizado.
4. Defina o campo **Ordem** para controlar a sequência de exibição. Apenas os itens listados serão mostrados para não-superusuários.

Quando não houver configuração ativa (ou caso ocorra algum erro ao montar o menu), o comportamento padrão do Django Admin é mantido automaticamente.
