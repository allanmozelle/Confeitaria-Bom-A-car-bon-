from django.shortcuts import render


def cardapio(request):
    return render(request, 'produtos/cardapio.html')


def detalhes(request, id):
    return render(request, 'produtos/detalhes.html')


def cadastrar(request):
    return render(request, 'produtos/cadastrar.html')


def editar(request):
    return render(request, 'produtos/editar.html')


def categorias(request):
    return render(request, 'produtos/categorias.html')