from django.shortcuts import render


def carrinho(request):
    return render(request, 'pedidos/carrinho.html')


def finalizar(request):
    return render(request, 'pedidos/finalizar.html')


def meus_pedidos(request):
    return render(request, 'pedidos/meus_pedidos.html')


def detalhes(request):
    return render(request, 'pedidos/detalhes.html')


def painel(request):
    return render(request, 'pedidos/painel.html')