from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.LoginPersonalizado.as_view(), name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
]
