from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        ordering = ['nome']

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    sku = models.CharField(max_length=20, unique=True, null=True, blank=True) # Código do produto
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')
    quantidade = models.PositiveIntegerField(default=0)
    preco = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.nome} ({self.quantidade})"

    def clean(self):
        if self.quantidade < 0:
            raise ValidationError("O estoque não pode ser negativo.")

class Movimentacao(models.Model):
    TIPO_CHOICES = (
        ('E', 'Entrada'),
        ('S', 'Saída'),
    )

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimentacoes', verbose_name="Responsável (Logado)")
    # Dados do solicitante
    solicitante_nome = models.CharField(max_length=100, blank=True)
    solicitante_cpf = models.CharField(max_length=14, blank=True, null=True) # Ex: 000.000.000-00
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome} - {self.quantidade}"

    def clean(self):
        if not self.produto_id or not self.quantidade:
            return

        # LÓGICA DE NEGÓCIO: Validação do Limite de 3 Retiradas
        if self.tipo == 'S' and not self.pk: # Apenas se for Saída e for Novo registro
            # Verifica se o que tem no banco é menor do que o que se quer tirar
            if self.produto.quantidade < self.quantidade:
                raise ValidationError({
                    'quantidade': f'Estoque insuficiente. Disponível: {self.produto.quantidade}.'
                })
            
            # hoje_inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

            # VERIFICAR =======================================================
    
            # # Conta quantas saídas esse CPF já fez hoje (excluio a atual se for edição)
            # saidas_hoje = Movimentacao.objects.filter(
            #     tipo='S',
            #     solicitante_cpf=self.solicitante_cpf,
            #     created_at__gte=hoje_inicio
            # ).count()

            # # Se for uma criação nova e já tiver 3, bloqueia.
            # if not self.pk and saidas_hoje >= 3:
            #     raise ValidationError(f"O CPF {self.solicitante_cpf} já atingiu o limite de 3 retiradas hoje.")

    def save(self, *args, **kwargs):
        # Executa as validações (o clean não roda automaticamente no save por padrão)
        self.full_clean()
        
        # Atualiza o estoque do produto automaticamente
        # Nota: Em um sistema real de alta concorrência, usaríamos F() expressions ou Signals
        super().save(*args, **kwargs) 
        
        # Recalcula o saldo do produto (Simples e Seguro)
        entradas = self.produto.movimentacoes.filter(tipo='E').aggregate(models.Sum('quantidade'))['quantidade__sum'] or 0
        saidas = self.produto.movimentacoes.filter(tipo='S').aggregate(models.Sum('quantidade'))['quantidade__sum'] or 0
        
        novo_saldo = entradas - saidas

        # Proteção extra: Se o recálculo der negativo (ex: apagaram uma entrada antiga), lança erro
        if novo_saldo < 0:
            raise ValidationError(f"Operação inválida. Isso deixaria o produto {self.produto.nome} com saldo negativo ({novo_saldo}).")
        
        self.produto.quantidade = novo_saldo
        self.produto.save()
    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        ordering = ['-created_at']