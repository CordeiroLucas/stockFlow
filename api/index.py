import os
from django.core.wsgi import get_wsgi_application

# Aponta para o seu settings (ajuste se o nome da pasta for diferente de 'core')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = get_wsgi_application()
