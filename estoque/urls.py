from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('movimentacao/', views.registrar_movimentacao, name='registrar_movimentacao'),
    path('saida-rapida/', views.registrar_saida_rapida, name='registrar_saida_rapida'), # Nova rota
    path('historico/', views.historico_movimentacoes, name='historico'),
    path('exportar/', views.exportar_relatorio, name='exportar_relatorio'),
]