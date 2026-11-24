from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from usuarios.decorators import funcionario_required

from .forms import CategoriaForm, ProdutoForm
from .models import Categoria, Produto


# ---------------------------------------------------------------------------
# Cardápio (cliente e funcionário)
# ---------------------------------------------------------------------------

def cardapio(request):
    produtos = Produto.objects.select_related('categoria').order_by('-disponivel', 'nome')

    categoria_atual = None
    categoria_id = request.GET.get('categoria', '')
    if categoria_id.isdigit():
        categoria_atual = int(categoria_id)
        produtos = produtos.filter(categoria_id=categoria_atual)

    contexto = {
        'produtos': produtos,
        'categorias': Categoria.objects.all(),
        'categoria_atual': categoria_atual,
    }
    return render(request, 'produtos/cardapio.html', contexto)


def detalhes(request, id):
    produto = get_object_or_404(Produto.objects.select_related('categoria'), id=id)
    return render(request, 'produtos/detalhes.html', {'produto': produto})


# ---------------------------------------------------------------------------
# Gerenciamento de produtos (somente funcionário)
# ---------------------------------------------------------------------------

@funcionario_required
def cadastrar(request):
    if not Categoria.objects.exists():
        messages.warning(request, 'Cadastre ao menos uma categoria antes de cadastrar produtos.')
        return redirect('produtos:categorias')

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            messages.success(request, f'Produto "{produto.nome}" cadastrado com sucesso.')
            return redirect('produtos:cardapio')
    else:
        form = ProdutoForm()

    return render(request, 'produtos/cadastrar.html', {'form': form})


@funcionario_required
def editar(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso.')
            return redirect('produtos:cardapio')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'produtos/editar.html', {'form': form, 'produto': produto})


@funcionario_required
@require_POST
def excluir(request, id):
    produto = get_object_or_404(Produto, id=id)
    nome = produto.nome
    if produto.imagem:
        produto.imagem.delete(save=False)  # apaga o arquivo da pasta media/
    produto.delete()
    messages.success(request, f'Produto "{nome}" excluído.')
    return redirect('produtos:cardapio')


@funcionario_required
@require_POST
def alternar_disponibilidade(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.disponivel = not produto.disponivel
    produto.save(update_fields=['disponivel'])
    situacao = 'disponível' if produto.disponivel else 'indisponível'
    messages.success(request, f'"{produto.nome}" agora está {situacao}.')
    if request.POST.get('voltar') == 'detalhes':
        return redirect('produtos:detalhes', id=produto.id)
    return redirect('produtos:cardapio')


# ---------------------------------------------------------------------------
# Gerenciamento de categorias (somente funcionário)
# ---------------------------------------------------------------------------

def _renderizar_categorias(request, form, categoria_editando=None):
    contexto = {
        'form': form,
        'categoria_editando': categoria_editando,
        'categorias': Categoria.objects.annotate(total=Count('produtos')),
    }
    return render(request, 'produtos/categorias.html', contexto)


@funcionario_required
def categorias(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" criada.')
            return redirect('produtos:categorias')
    else:
        form = CategoriaForm()

    return _renderizar_categorias(request, form)


@funcionario_required
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria "{categoria.nome}" atualizada.')
            return redirect('produtos:categorias')
    else:
        form = CategoriaForm(instance=categoria)

    return _renderizar_categorias(request, form, categoria_editando=categoria)


@funcionario_required
@require_POST
def excluir_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if categoria.produtos.exists():
        messages.error(
            request,
            f'Não é possível excluir "{categoria.nome}": ainda existem produtos nessa categoria.',
        )
    else:
        categoria.delete()
        messages.success(request, f'Categoria "{categoria.nome}" excluída.')

    return redirect('produtos:categorias')
