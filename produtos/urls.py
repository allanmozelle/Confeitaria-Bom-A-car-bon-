from django.urls import path

from . import views

urlpatterns = [
    path('', views.cardapio, name='cardapio'),
    path('<int:id>/', views.detalhes, name='detalhes'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('editar/', views.editar, name='editar'),
    path('categorias/', views.categorias, name='categorias'),
]