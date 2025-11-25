import os
import django
import random

# 1. Configura o ambiente Django para que o script possa acessar o banco
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# 2. Importa os Models (só funciona depois do django.setup())
from estoque.models import Categoria, Produto


def popular():
    print("🚀 Iniciando povoamento do banco de dados...\n")

    # Estrutura de dados solicitada
    dados = {
        "Cookies": [],
        "Cervejas": [],
        "Refrigerantes": ["Guaraná", "Pepsi Zero"],
        "Capsulas": [],
        "Salgadinho": [
            "Cheetos",
            "Cebolitos",
            "Doritos",
            "Torcida Churrasco",
            "Torcida Costela c Limao",
        ],
    }

    for categoria_nome, produtos_lista in dados.items():
        # A. Cria ou Pega a Categoria (evita duplicatas)
        categoria, created = Categoria.objects.get_or_create(nome=categoria_nome)

        status_cat = "✅ Criada" if created else "ℹ️ Já existe"
        print(f"{status_cat}: Categoria '{categoria_nome}'")

        # B. Cria os Produtos dessa Categoria
        for produto_nome in produtos_lista:
            # Gera um SKU aleatório para garantir unicidade (Ex: SAL-1234)
            prefixo = categoria_nome[:3].upper()
            sku_gerado = f"{prefixo}-{random.randint(1000, 9999)}"

            # get_or_create verifica pelo nome. Se não existir, usa os 'defaults' para criar.
            produto, prod_created = Produto.objects.get_or_create(
                nome=produto_nome,
                defaults={
                    "categoria": categoria,
                    "preco": 5.00,  # Preço fictício
                    "sku": sku_gerado,
                },
            )

            if prod_created:
                print(f"   └── ➕ Produto criado: {produto_nome} (SKU: {sku_gerado})")
            else:
                # Se o produto já existe, atualizamos a categoria para garantir que está certa
                if produto.categoria != categoria:
                    produto.categoria = categoria
                    produto.save()
                    print(
                        f"   └── 🔄 Atualizado: {produto_nome} movido para {categoria_nome}"
                    )
                else:
                    print(f"   └── ℹ️ Já existe: {produto_nome}")

    print("\n✨ Concluído! O banco de dados foi populado com sucesso.")


if __name__ == "__main__":
    popular()
