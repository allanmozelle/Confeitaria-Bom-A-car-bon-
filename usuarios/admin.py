from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Usuario


class UsuarioCriacaoForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'nome_completo', 'email', 'tipo')


class UsuarioEdicaoForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = '__all__'


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """É aqui que a administração cria as contas de FUNCIONÁRIOS (tipo = Funcionário)."""

    form = UsuarioEdicaoForm
    add_form = UsuarioCriacaoForm

    list_display = ('username', 'nome_completo', 'email', 'tipo', 'is_active')
    list_filter = ('tipo', 'is_active', 'is_staff')
    search_fields = ('username', 'nome_completo', 'email')
    ordering = ('nome_completo',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Dados pessoais', {'fields': ('nome_completo', 'email')}),
        ('Tipo de usuário', {'fields': ('tipo',)}),
        ('Permissões', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
        )}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nome_completo', 'email', 'tipo', 'password1', 'password2'),
        }),
    )
