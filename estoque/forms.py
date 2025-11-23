from django import forms
from django.core.exceptions import ValidationError
from .models import Movimentacao
import re

# Função auxiliar para calcular o dígito verificador
def calcular_digito(cpf, peso):
    soma = 0
    for i, n in enumerate(cpf):
        soma += int(n) * peso[i]
    resto = soma % 11
    return '0' if resto < 2 else str(11 - resto)

def is_cpf_valido(cpf):
    # Remove tudo que não for número
    cpf = re.sub(r'\D', '', cpf)

    # Verifica tamanho e se todos os números são iguais (ex: 111.111.111-11)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    # Validação do 1º Dígito
    peso1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    primeiro_digito = calcular_digito(cpf[:9], peso1)
    if cpf[9] != primeiro_digito:
        return False

    # Validação do 2º Dígito
    peso2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    segundo_digito = calcular_digito(cpf[:10], peso2)
    if cpf[10] != segundo_digito:
        return False

    return True

class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['produto', 'tipo', 'quantidade', 'solicitante_nome', 'solicitante_cpf']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'solicitante_nome': forms.TextInput(attrs={'class': 'form-control'}),
            # Adicionamos um ID específico aqui para o Javascript pegar
            'solicitante_cpf': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cpf', 'placeholder': '000.000.000-00', 'maxlength': '14'}),
        }

    def clean_solicitante_cpf(self):
        cpf_original = self.cleaned_data.get('solicitante_cpf')
        
        # Se o CPF for opcional e estiver vazio, retorna vazio (sem erro)
        if not cpf_original:
            return None
            
        # Remove caracteres para validar
        cpf_limpo = re.sub(r'\D', '', cpf_original)
        
        if not is_cpf_valido(cpf_limpo):
            raise ValidationError("CPF inválido. Verifique os números digitados.")
            
        return cpf_limpo # Retorna o CPF limpo (apenas números) para o banco
    
class SaidaRapidaForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['produto', 'quantidade'] # Removemos CPF, Nome e Tipo
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select form-select-lg', 'aria-label': 'Selecione o produto'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control form-control-lg text-center', 'inputmode': 'numeric'}),
        }