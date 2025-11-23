from django.contrib import admin
from .models import Produto, Movimentacao

class MovimentacaoInline(admin.TabularInline):
    model = Movimentacao
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'sku')
    search_fields = ('nome',)
    inlines = [MovimentacaoInline] # Permite ver o histórico dentro do produto

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'solicitante_nome', 'solicitante_cpf', 'created_at')
    list_filter = ('tipo', 'created_at')
    search_fields = ('produto__nome', 'solicitante_cpf')