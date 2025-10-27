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
