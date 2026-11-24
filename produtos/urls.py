from django.urls import path

from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.cardapio, name='cardapio'),
    path('<int:id>/', views.detalhes, name='detalhes'),

    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('<int:id>/editar/', views.editar, name='editar'),
    path('<int:id>/excluir/', views.excluir, name='excluir'),
    path('<int:id>/disponibilidade/', views.alternar_disponibilidade, name='disponibilidade'),

    path('categorias/', views.categorias, name='categorias'),
    path('categorias/<int:id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:id>/excluir/', views.excluir_categoria, name='excluir_categoria'),
]
