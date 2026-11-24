def carrinho_quantidade(request):
    """Disponibiliza `carrinho_quantidade` em todos os templates (mostrado no menu)."""
    usuario = getattr(request, 'user', None)
    if usuario is not None and usuario.is_authenticated and usuario.eh_cliente:
        return {'carrinho_quantidade': sum(request.session.get('carrinho', {}).values())}
    return {}
