from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Produto, Movimentacao
from .forms import MovimentacaoForm, SaidaRapidaForm

import csv
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    produtos = Produto.objects.all().order_by('nome')
    return render(request, 'estoque/dashboard.html', {'produtos': produtos})

@login_required
def registrar_movimentacao(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            try:
                form.save() # Aqui ele chama o clean() do model e valida as 3 saídas!
                messages.success(request, "Movimentação registrada com sucesso!")
                return redirect('dashboard')
            except Exception as e:
                # Caso passe pelo form mas falhe no model (extra safety)
                messages.error(request, f"Erro ao salvar: {e}")
    else:
        form = MovimentacaoForm()

    return render(request, 'estoque/form_movimentacao.html', {'form': form})

@login_required
def historico_movimentacoes(request):
    # Começa pegando TUDO, ordenado do mais recente para o mais antigo
    movimentacoes = Movimentacao.objects.all().select_related('produto').order_by('-created_at')
    
    # Captura os filtros do formulário (se houver)
    busca_produto = request.GET.get('produto')
    busca_tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Aplica os filtros SE eles existirem
    if busca_produto:
        movimentacoes = movimentacoes.filter(produto__nome__icontains=busca_produto)
    
    if busca_tipo:
        movimentacoes = movimentacoes.filter(tipo=busca_tipo)
        
    if data_inicio:
        movimentacoes = movimentacoes.filter(created_at__date__gte=data_inicio)
        
    if data_fim:
        movimentacoes = movimentacoes.filter(created_at__date__lte=data_fim)

    context = {
        'movimentacoes': movimentacoes,
        # Passamos os valores de volta para manter o formulário preenchido após a busca
        'filtros': request.GET 
    }
    
    return render(request, 'estoque/historico.html', context)

@login_required
def exportar_relatorio(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="relatorio_estoque.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=';')

    writer.writerow(['Data/Hora', 'Tipo', 'Produto', 'Quantidade', 'Solicitante', 'CPF'])

    # 1. Base da consulta
    movimentacoes = Movimentacao.objects.all().select_related('produto').order_by('-created_at')

    # 2. APLICAÇÃO DOS FILTROS (Igualzinho à view de histórico)
    busca_produto = request.GET.get('produto')
    busca_tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if busca_produto:
        movimentacoes = movimentacoes.filter(produto__nome__icontains=busca_produto)
    
    if busca_tipo:
        movimentacoes = movimentacoes.filter(tipo=busca_tipo)
        
    if data_inicio:
        movimentacoes = movimentacoes.filter(created_at__date__gte=data_inicio)
        
    if data_fim:
        movimentacoes = movimentacoes.filter(created_at__date__lte=data_fim)

    # 3. Escreve os dados filtrados
    for mov in movimentacoes:
        writer.writerow([
            mov.created_at.strftime('%d/%m/%Y %H:%M'),
            mov.get_tipo_display(),
            mov.produto.nome,
            mov.quantidade,
            mov.solicitante_nome or '-',
            mov.solicitante_cpf or '-'
        ])

    return response

@login_required
def registrar_saida_rapida(request):
    if request.method == 'POST':
            form = SaidaRapidaForm(request.POST)
            if form.is_valid():
                try:
                    # Cria o objeto mas não salva ainda
                    movimentacao = form.save(commit=False)
                    
                    # Define automaticamente como SAÍDA
                    movimentacao.tipo = 'S'
                    
                    # Define campos opcionais como vazios ou um valor padrão do sistema
                    movimentacao.solicitante_nome = "Saída Rápida (Mobile)"
                    movimentacao.solicitante_cpf = None 
                    
                    movimentacao.save()
                    messages.success(request, f"Saída de {movimentacao.quantidade}x {movimentacao.produto.nome} registrada!")
                    return redirect('registrar_saida_rapida') # Recarrega a mesma pág para agilizar a próxima
                except Exception as e:
                    messages.error(request, f"Erro ao registrar: {e}")
    else:
        form = SaidaRapidaForm()

    return render(request, 'estoque/saida_rapida.html', {'form': form})