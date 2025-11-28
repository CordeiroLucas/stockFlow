from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Produto, Movimentacao, Categoria
from .forms import MovimentacaoForm, SaidaRapidaForm

import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from django.db.models import Q, Sum
from django.db import transaction

@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('registrar_saida_rapida')

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
def recalcular_estoque(request):
    # 1. Segurança: Só admin pode fazer isso
    if not request.user.is_superuser:
        return redirect('registrar_saida_rapida')

    produtos = Produto.objects.all()
    atualizados = 0

    for produto in produtos:
        # Soma todas as Entradas
        total_entradas = produto.movimentacoes.filter(tipo='E').aggregate(Sum('quantidade'))['quantidade__sum'] or 0

        # Soma todas as Saídas
        total_saidas = produto.movimentacoes.filter(tipo='S').aggregate(Sum('quantidade'))['quantidade__sum'] or 0

        # Calcula o Saldo Real
        saldo_real = total_entradas - total_saidas

        # Proteção contra negativo (caso o banco tenha sido manipulado erradamente)
        if saldo_real < 0:
            saldo_real = 0

        # Atualiza apenas se houver divergência (para economizar processamento)
        if produto.quantidade != saldo_real:
            produto.quantidade = saldo_real
            produto.save()
            atualizados += 1

    if atualizados > 0:
        messages.warning(request, f"Sincronização concluída! {atualizados} produtos tiveram o saldo corrigido.")
    else:
        messages.success(request, "O estoque já estava 100% sincronizado.")

    return redirect('dashboard')

@login_required
def registrar_movimentacao(request):
    if not request.user.is_superuser:
        return redirect('registrar_saida_rapida')

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
    # 1. TRAVA DE SEGURANÇA (Mantendo o que fizemos antes)
    if not request.user.is_superuser:
        return redirect('saida_rapida')

    # 2. BASE DA CONSULTA
    movimentacoes = Movimentacao.objects.all().select_related('produto', 'produto__categoria').order_by('-created_at')
    
    # 3. FILTROS (Mantém a lógica existente)
    categorias = Categoria.objects.all() 
    busca_produto = request.GET.get('produto', '')
    busca_tipo = request.GET.get('tipo', '')
    busca_categoria = request.GET.get('categoria', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    if busca_produto:
        movimentacoes = movimentacoes.filter(produto__nome__icontains=busca_produto)
    if busca_tipo:
        movimentacoes = movimentacoes.filter(tipo=busca_tipo)
    if busca_categoria:
        movimentacoes = movimentacoes.filter(produto__categoria_id=busca_categoria)
    if data_inicio:
        movimentacoes = movimentacoes.filter(created_at__date__gte=data_inicio)
    if data_fim:
        movimentacoes = movimentacoes.filter(created_at__date__lte=data_fim)

    # 4. PAGINAÇÃO (AQUI É A NOVIDADE)
    paginator = Paginator(movimentacoes, 10) # 20 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj, # Enviamos o objeto paginado, não mais a lista completa
        'categorias': categorias,
        # Passamos o request.GET inteiro para facilitar o preenchimento do form
        'filtros': request.GET 
    }
    
    return render(request, 'estoque/historico.html', context)

@login_required
def exportar_relatorio(request):
    if not request.user.is_superuser:
        return redirect('registrar_saida_rapida')
    
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