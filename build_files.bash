#!/bin/bash

echo "🚀 Iniciando Build..."

# Instala as dependências (Vercel precisa do requirements.txt)
python3.12 -m pip install -r requirements.txt

# Roda o collectstatic na raiz mesmo
echo "🎨 Coletando arquivos estáticos..."
python3.12 manage.py collectstatic --noinput --clear

echo "✅ Build Concluído!"