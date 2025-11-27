#!/bin/bash

echo "🚀 Iniciando Build..."
# 2. Usamos 'python3' (o padrão do ambiente) em vez de forçar 'python3.9'
python3 -m pip install -r requirements.txt
echo "🎨 Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear

echo "✅ Build Concluído!"