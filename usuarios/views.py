from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.shortcuts import redirect, render, resolve_url

from .forms import CadastroForm, LoginForm



@login_not_required
class LoginPersonalizado(auth_views.LoginView):
    """Login por usuário ou e-mail, com redirecionamento conforme o tipo de usuário."""

    template_name = 'usuarios/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        if self.request.user.eh_funcionario:
            return resolve_url('pedidos:painel')
        return resolve_url('principal:home')


@login_not_required
def cadastro(request):
    if request.user.is_authenticated:
        return redirect('principal:home')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario, backend='usuarios.backends.EmailOuUsuarioBackend')
            messages.success(
                request,
                f'Conta criada com sucesso! Seja bem-vindo(a), {usuario.get_short_name()}.',
            )
            return redirect('principal:home')
    else:
        form = CadastroForm()

    return render(request, 'usuarios/cadastro.html', {'form': form})
