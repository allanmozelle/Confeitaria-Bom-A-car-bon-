from django.urls import path

from . import views

app_name = 'pedidos'

urlpatterns = [
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_carrinho'),
    path('carrinho/atualizar/<int:produto_id>/', views.atualizar_carrinho, name='atualizar_carrinho'),
    path('carrinho/remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_carrinho'),

    path('finalizar/', views.finalizar, name='finalizar'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('painel/', views.painel, name='painel'),

    path('<int:id>/', views.detalhes, name='detalhes'),
    path('<int:id>/status/', views.alterar_status, name='alterar_status'),
]
