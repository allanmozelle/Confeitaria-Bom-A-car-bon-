from django.urls import path

from . import views

urlpatterns = [
    path('carrinho/', views.carrinho, name='carrinho'),
    path('finalizar/', views.finalizar, name='finalizar'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('<int:id>/', views.detalhes, name='detalhes'),
    path('painel/', views.painel, name='painel'),
]