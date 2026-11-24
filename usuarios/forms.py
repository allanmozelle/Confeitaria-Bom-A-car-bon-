from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário ou e-mail',
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Digite seu usuário ou e-mail',
        }),
    )
    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'}),
    )

    error_messages = {
        'invalid_login': 'Usuário/e-mail ou senha incorretos.',
        'inactive': 'Esta conta está inativa.',
    }


class CadastroForm(UserCreationForm):
    """Cadastro público: cria SEMPRE um cliente (o tipo não aparece no formulário)."""

    class Meta:
        model = Usuario
        fields = ['nome_completo', 'email', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome_completo'].widget.attrs['placeholder'] = 'Digite seu nome completo'
        self.fields['email'].widget.attrs['placeholder'] = 'Digite seu e-mail'
        self.fields['username'].label = 'Nome de usuário'
        self.fields['username'].widget.attrs['placeholder'] = 'Escolha um nome de usuário'
        self.fields['password1'].label = 'Senha'
        self.fields['password1'].widget.attrs['placeholder'] = 'Crie uma senha'
        self.fields['password2'].label = 'Confirmar senha'
        self.fields['password2'].widget.attrs['placeholder'] = 'Digite sua senha novamente'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo = Usuario.CLIENTE
        if commit:
            usuario.save()
        return usuario
