from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Produto, Movimentacao, Categoria
from .forms import MovimentacaoForm, SaidaRapidaForm

import csv
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from django.db.models import Q
from django.db import transaction
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    # 1. Começa com todos os produtos
    # O select_related('categoria') é vital para performance (evita N+1 queries)
    produtos_list = Produto.objects.all().select_related('categoria').order_by('nome')
    
    # 2. Captura os dados do GET (da URL)
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('categoria', '')

    # 3. Aplica Filtro por Nome ou SKU
    if search_query:
        produtos_list = produtos_list.filter(
            Q(nome__icontains=search_query) | 
            Q(sku__icontains=search_query)
        )

    # 4. Aplica Filtro por Categoria
    if category_id:
        produtos_list = produtos_list.filter(categoria_id=category_id)

    # 5. Paginação (Aplica APÓS filtrar)
    paginator = Paginator(produtos_list, 10) # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 6. Busca categorias para preencher o dropdown
    categorias = Categoria.objects.all()

    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        # Passamos os filtros de volta para manter os campos preenchidos na tela
        'search_query': search_query, 
        'category_id': int(category_id) if category_id else '' 
    }

    return render(request, 'estoque/dashboard.html', context)

@login_required
def registrar_movimentacao(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic(): 
                    form.save()

                messages.success(request, "Movimentação registrada com sucesso!")
                return redirect('dashboard')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = MovimentacaoForm()
        
    produtos_data = Produto.objects.all().values('id', 'nome', 'quantidade', 'categoria_id').order_by('nome')

    context = {
        'form': form,
        'produtos_data': list(produtos_data) # Envia para o template
    }

    return render(request, 'estoque/form_movimentacao.html', context)

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
                # BLINDAGEM
                with transaction.atomic():
                    movimentacao = form.save(commit=False)
                    movimentacao.tipo = 'S'
                    movimentacao.solicitante_nome = "Saída Rápida (Mobile)"
                    movimentacao.solicitante_cpf = None
                    movimentacao.save() # Se isso gerar erro de saldo, o 'atomic' desfaz a criação

                messages.success(request, f"Saída de {movimentacao.quantidade}x {movimentacao.produto.nome} registrada!")
                return redirect('registrar_saida_rapida')

            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = SaidaRapidaForm()

    produtos_data = Produto.objects.all().values('id', 'nome', 'quantidade', 'categoria_id').order_by('nome')

    context = {
        'form': form,
        'produtos_data': list(produtos_data) # Convertemos para lista para o JS ler
    }

    return render(request, 'estoque/saida_rapida.html', context)