#!/bin/bash

echo "🚀 Iniciando Build..."
python3 -m pip install -r requirements.txt

# 2. Usamos 'python3' (o padrão do ambiente) em vez de forçar 'python3.9'
echo "🎨 Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear

echo "✅ Build Concluído!"