from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def funcionario_required(view):
    """Só deixa funcionários acessarem a página (cliente é mandado de volta ao início)."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.eh_funcionario:
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('principal:home')
        return view(request, *args, **kwargs)

    return wrapper


def cliente_required(view):
    """Só deixa clientes acessarem (carrinho e pedidos são exclusivos do cliente)."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.eh_cliente:
            messages.error(request, 'Esta área é exclusiva para clientes.')
            return redirect('pedidos:painel')
        return view(request, *args, **kwargs)

    return wrapper
