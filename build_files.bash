#!/bin/bash

echo "🚀 Iniciando Build..."

pip install -r requirements.txt

echo "🎨 Coletando arquivos estáticos..."

python manage.py collectstatic --noinput

echo "✅ Build Concluído!"