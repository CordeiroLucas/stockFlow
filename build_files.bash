#!/bin/bash

echo "🚀 Iniciando Build..."

python3.9 -m pip install -r requirements.txt
python3.9 manage.py collectstatic --noinput --clear

echo "✅ Build Concluído!"