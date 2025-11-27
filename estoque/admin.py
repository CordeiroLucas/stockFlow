from django.contrib import admin
from django.utils.html import format_html
from .models import Produto, Movimentacao, Categoria

# 1. Configuração da Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'total_produtos')
    search_fields = ('nome',)
    
    def total_produtos(self, obj):
        return obj.produtos.count()
    total_produtos.short_description = 'Qtd Produtos'

# 2. Configuração Inline (Histórico dentro do Produto)
class MovimentacaoInline(admin.TabularInline):
    model = Movimentacao
    extra = 0
    readonly_fields = ('tipo_badge', 'quantidade', 'solicitante_nome', 'created_at')
    fields = ('created_at', 'tipo_badge', 'quantidade', 'solicitante_nome')
    can_delete = False # Histórico não deve ser apagado facilmente
    max_num = 0 # Impede adicionar movimentação por aqui (força usar a tela correta)
    
    def tipo_badge(self, obj):
        color = 'green' if obj.tipo == 'E' else 'red'
        label = 'Entrada' if obj.tipo == 'E' else 'Saída'
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 10px; font-weight: bold;">{}</span>',
            color, label
        )
    tipo_badge.short_description = 'Tipo'

# 3. Configuração do Produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'sku', 'status_estoque', 'preco')
    list_filter = ('categoria', 'quantidade') # Filtro lateral
    search_fields = ('nome', 'sku')
    readonly_fields = ('quantidade',) # Quantidade é calculada, ninguém mexe!
    inlines = [MovimentacaoInline]
    list_per_page = 20

    # Organização visual do formulário de edição
    fieldsets = (
        ('Dados Principais', {
            'fields': ('nome', 'categoria', 'sku')
        }),
        ('Estoque e Valores', {
            'fields': ('quantidade', 'preco'),
            'classes': ('collapse',) # Deixa essa área recolhível se quiser
        }),
    )

    # Função para colorir o estoque
    def status_estoque(self, obj):
        if obj.quantidade == 0:
            color = 'red'
            val = 'Zerado'
        elif obj.quantidade < 5:
            color = 'orange'
            val = f'{obj.quantidade} (Baixo)'
        else:
            color = 'green'
            val = f'{obj.quantidade} uni'
            
        return format_html(
            '<b style="color: {};">{}</b>',
            color, val
        )
    status_estoque.short_description = 'Estoque Atual'

# 4. Configuração da Movimentação (Log Geral)
@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('data_formatada', 'badge_tipo', 'produto', 'quantidade', 'solicitante_info')
    list_filter = ('tipo', 'created_at', 'produto__categoria') # Filtros poderosos
    search_fields = ('produto__nome', 'solicitante_nome', 'solicitante_cpf')
    date_hierarchy = 'created_at' # Cria uma navegação por data no topo
    
    # Como é um log, sugerimos deixar tudo readonly para auditoria
    def has_add_permission(self, request):
        return False # Obriga a usar o Dashboard/App para criar, não o Admin

    def has_delete_permission(self, request, obj=None):
        return False # Impede apagar histórico pelo admin (Segurança)

    def data_formatada(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    data_formatada.short_description = 'Data/Hora'

    def badge_tipo(self, obj):
        if obj.tipo == 'E':
            return format_html('<span style="color:green;">⬇ Entrada</span>')
        return format_html('<span style="color:red;">⬆ Saída</span>')
    badge_tipo.short_description = 'Operação'

    def solicitante_info(self, obj):
        if obj.solicitante_nome:
            return f"{obj.solicitante_nome} ({obj.solicitante_cpf or 'S/ CPF'})"
        return "-"
    solicitante_info.short_description = 'Responsável'