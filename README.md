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

### Recursos do Admin (JS-only)
Herde de `BaseAdmin` (para `ModelAdmin`) e `BaseInline` (para inlines) definidos em `core/admin.py`. O mixin `Select2AdminMixin` carrega automaticamente:

- o Select2 via CDN;
- `apiary/js/hive_species_filter.js` (ponto de configuração dos selects);
- `apiary/js/conditional-fields.js` (engine de campos condicionais);
- `apiary/js/image-preview.js` e `apiary/css/image-preview.css` (prévia de imagens).

Resumo rápido:

- [Prévia de imagem](/docs/preview-image.md) — adicione `data-admin-preview="image"` nos `input[type=file]` que devem exibir miniatura.
- [Campos condicionais](/docs/campos-condicionais.md) — declare `window.ADMIN_FIELD_RULES` com regras `when/then` por sufixo do campo.
- [Select2](/docs/select2.md) — use `data-select2="1"` ou configure `window.SELECT2_START` para definir os seletores desejados.

### Tema Django utilizado - Django admin interface:
Clique [aqui](https://github.com/fabiocaccamo/django-admin-interface?tab=readme-ov-file) para ver o tema utilizado neste projeto.

### Menu personalizado do Django Admin

Superusuários continuam visualizando o menu padrão do Django. Para usuários não-super é possível definir menus específicos por escopo (grupos ou o padrão "Não superusuários") seguindo os passos abaixo:

1. No admin, acesse **Menu do Admin → Escopos** e cadastre os escopos desejados:
   - Informe um **Nome** amigável.
   - Opcionalmente relacione um **Grupo** do Django. Usuários pertencentes ao grupo utilizarão o menu desse escopo.
   - Utilize o campo **Prioridade** para desempate quando um usuário participar de mais de um grupo (valores maiores têm precedência).
   - Garanta que exista um escopo sem grupo para servir como fallback para todos os demais usuários não-super.
2. Em **Menu do Admin → Configurações de menu**, crie uma configuração para cada escopo e marque **Ativa** na opção que deve valer. Apenas uma configuração fica ativa por escopo.
3. Cadastre os itens diretamente no inline "Itens de menu":
   - **Modelo**: informe `app_label` e `model_name` (em minúsculo). As permissões padrão do admin continuam valendo.
   - **Link personalizado**: informe um `Nome da URL` (ex.: `dashboard:index`) ou uma `URL absoluta`. O campo `Permissão extra` aceita `app_label.codename` quando o link exigir uma permissão específica.
   - Utilize o campo **Seção** para agrupar itens sob um título customizado (ex.: “Operações”). Quando vazio, o nome do aplicativo ou "Links" é utilizado.
   - Ajuste **Ordem** para controlar a sequência de exibição dentro do menu.

Quando o usuário não possuir escopo configurado (ou quando nenhuma configuração ativa estiver disponível), o menu volta automaticamente para o comportamento padrão do Django Admin.
