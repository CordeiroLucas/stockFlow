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
    list_display = ('nome', 'categoria', 'quantidade', 'sku', 'status_estoque')
    list_filter = ('categoria',)
    search_fields = ('nome', 'sku')
    
    # O SKU agora é somente leitura, assim como a Quantidade
    readonly_fields = ('quantidade', 'sku') 
    
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
    list_display = ('data_formatada', 'badge_tipo', 'produto', 'quantidade', 'usuario', 'solicitante_info', 'observacao_curta')
    list_filter = ('tipo', 'usuario', 'created_at', 'produto__categoria')
    search_fields = ('produto__nome', 'solicitante_nome', 'solicitante_cpf')
    date_hierarchy = 'created_at'
    
    # Define quais campos aparecem no formulário de criação
    fields = ('tipo', 'produto', 'quantidade', 'solicitante_nome', 'solicitante_cpf', 'observacao')

    # --- 1. SEGURANÇA: Captura o Admin Logado ---
    def save_model(self, request, obj, form, change):
        """
        Esse método roda antes de salvar no banco pelo Admin.
        Aqui injetamos o usuário logado automaticamente.
        """
        # Se o campo usuário estiver vazio (sempre estará na criação via admin)
        if not obj.usuario:
            obj.usuario = request.user
            
        # Se não preencheu o destinatário, marcamos como Ajuste Administrativo
        if not obj.solicitante_nome:
            obj.solicitante_nome = f"Ajuste Admin ({request.user.username})"
            
        super().save_model(request, obj, form, change)

    # --- 2. PERMISSÕES: Histórico Imutável ---
    
    def has_add_permission(self, request):
        return True # Permite criar estornos/ajustes

    def has_change_permission(self, request, obj=None):
        return False # Bloqueia edição de passado

    def has_delete_permission(self, request, obj=None):
        return False # Bloqueia apagar histórico

    # --- 3. VISUALIZAÇÃO ---
    
    def get_readonly_fields(self, request, obj=None):
        if obj: # Se for visualização, trava tudo
            return [f.name for f in self.model._meta.fields]
        return []

    # Métodos de formatação visual (Badges, Datas, etc)
    def data_formatada(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    data_formatada.short_description = 'Data/Hora'

    def badge_tipo(self, obj):
        if obj.tipo == 'E':
            return format_html('<span style="color:green; font-weight:bold;">⬇ Entrada</span>')
        return format_html('<span style="color:red; font-weight:bold;">⬆ Saída</span>')
    badge_tipo.short_description = 'Operação'

    def solicitante_info(self, obj):
        return f"{obj.solicitante_nome or '-'} {obj.solicitante_cpf or ''}"
    solicitante_info.short_description = 'Destinatário'

    def observacao_curta(self, obj):
        if obj.observacao:
            return (obj.observacao[:30] + '..') if len(obj.observacao) > 30 else obj.observacao
        return "-"
    observacao_curta.short_description = 'Obs'
    list_display = ('data_formatada', 'badge_tipo', 'produto', 'quantidade', 'usuario', 'solicitante_info', 'observacao_curta')
    list_filter = ('tipo', 'usuario', 'created_at', 'produto__categoria')
    search_fields = ('produto__nome', 'solicitante_nome', 'solicitante_cpf')
    date_hierarchy = 'created_at'
    
    def observacao_curta(self, obj):
        if obj.observacao:
            return (obj.observacao[:30] + '..') if len(obj.observacao) > 30 else obj.observacao
        return "-"
    observacao_curta.short_description = 'Obs'

    # 1. PERMISSÕES: Garantir a Integridade do Histórico
    
    def has_add_permission(self, request):
        # Permite criar novas movimentações (para fins de ajuste/estorno)
        return True

    def has_change_permission(self, request, obj=None):
        # PROIBIDO: Não pode alterar nada que já foi salvo
        return False

    def has_delete_permission(self, request, obj=None):
        # PROIBIDO: Não pode apagar histórico
        return False

    # 2. VISUALIZAÇÃO: Transformar campos em texto ao visualizar
    
    def get_readonly_fields(self, request, obj=None):
        # Se 'obj' existe, significa que estamos visualizando um registro antigo.
        # Nesse caso, TODOS os campos ficam somente-leitura.
        if obj:
            return [f.name for f in self.model._meta.fields]
        # Se 'obj' é None, estamos criando um novo, então deixa editar.
        return []

    # 3. MÉTODOS VISUAIS (Badges e Formatação)
    
    def data_formatada(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    data_formatada.short_description = 'Data/Hora'

    def badge_tipo(self, obj):
        if obj.tipo == 'E':
            return format_html('<span style="color:green; font-weight:bold;">⬇ Entrada</span>')
        return format_html('<span style="color:red; font-weight:bold;">⬆ Saída</span>')
    badge_tipo.short_description = 'Operação'

    def solicitante_info(self, obj):
        if obj.solicitante_nome:
            cpf = obj.solicitante_cpf or 'S/ CPF'
            return f"{obj.solicitante_nome} ({cpf})"
        return "-"
    solicitante_info.short_description = 'Destino'