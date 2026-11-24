from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from produtos.models import Produto
from usuarios.decorators import cliente_required, funcionario_required

from .carrinho import Carrinho
from .forms import FinalizarPedidoForm
from .models import ItemPedido, Pedido


def _quantidade(request, padrao=1):
    """Lê e valida o campo 'quantidade' enviado pelo formulário."""
    try:
        return max(1, int(request.POST.get('quantidade', padrao)))
    except (TypeError, ValueError):
        return padrao


# ---------------------------------------------------------------------------
# Carrinho (somente cliente)
# ---------------------------------------------------------------------------

@cliente_required
def carrinho(request):
    carrinho = Carrinho(request)
    itens = carrinho.itens()
    contexto = {
        'itens': itens,
        'total': carrinho.total(itens),
        'tem_indisponivel': any(not i['disponivel'] for i in itens),
    }
    return render(request, 'pedidos/carrinho.html', contexto)


@cliente_required
@require_POST
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if not produto.disponivel:
        messages.error(request, f'"{produto.nome}" está indisponível no momento.')
        return redirect('produtos:detalhes', id=produto.id)

    Carrinho(request).adicionar(produto, _quantidade(request))
    messages.success(request, f'"{produto.nome}" foi adicionado ao carrinho.')
    return redirect('pedidos:carrinho')


@cliente_required
@require_POST
def atualizar_carrinho(request, produto_id):
    Carrinho(request).atualizar(produto_id, _quantidade(request))
    messages.success(request, 'Quantidade atualizada.')
    return redirect('pedidos:carrinho')


@cliente_required
@require_POST
def remover_do_carrinho(request, produto_id):
    Carrinho(request).remover(produto_id)
    messages.success(request, 'Produto removido do carrinho.')
    return redirect('pedidos:carrinho')


# ---------------------------------------------------------------------------
# Finalização e acompanhamento (cliente)
# ---------------------------------------------------------------------------

@cliente_required
def finalizar(request):
    carrinho = Carrinho(request)
    itens = carrinho.itens()

    if not itens:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('pedidos:carrinho')

    indisponiveis = [i['produto'].nome for i in itens if not i['disponivel']]
    if indisponiveis:
        messages.error(
            request,
            'Remova os produtos indisponíveis antes de finalizar: ' + ', '.join(indisponiveis) + '.',
        )
        return redirect('pedidos:carrinho')

    if request.method == 'POST':
        form = FinalizarPedidoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                pedido = form.save(commit=False)
                pedido.cliente = request.user
                pedido.valor_total = carrinho.total(itens)  # calculado no servidor
                pedido.save()
                ItemPedido.objects.bulk_create([
                    ItemPedido(
                        pedido=pedido,
                        produto=item['produto'],
                        nome_produto=item['produto'].nome,
                        quantidade=item['quantidade'],
                        preco_unitario=item['produto'].preco,  # preço no momento da compra
                    )
                    for item in itens
                ])
            carrinho.limpar()
            messages.success(request, f'Pedido {pedido.codigo} realizado com sucesso!')
            return redirect('pedidos:detalhes', id=pedido.id)
    else:
        form = FinalizarPedidoForm()

    contexto = {'form': form, 'itens': itens, 'total': carrinho.total(itens)}
    return render(request, 'pedidos/finalizar.html', contexto)


@cliente_required
def meus_pedidos(request):
    pedidos = (
        Pedido.objects.filter(cliente=request.user)
        .prefetch_related('itens')
        .order_by('-data')
    )
    return render(request, 'pedidos/meus_pedidos.html', {'pedidos': pedidos})


@login_required
def detalhes(request, id):
    """Cliente vê só os próprios pedidos; funcionário vê qualquer pedido."""

    pedidos = Pedido.objects.select_related('cliente').prefetch_related('itens')

    if request.user.eh_funcionario:
        pedido = get_object_or_404(pedidos, id=id)
    else:
        pedido = get_object_or_404(pedidos, id=id, cliente=request.user)

    contexto = {'pedido': pedido, 'opcoes_status': Pedido.STATUS}

    return render(request, 'pedidos/detalhes.html', contexto)

# ---------------------------------------------------------------------------
# Área do funcionário
# ---------------------------------------------------------------------------

@funcionario_required
def painel(request):
    por_status = dict(
        Pedido.objects.values_list('status').annotate(total=Count('id'))
    )
    resumo = {
        'pendentes': por_status.get(Pedido.PENDENTE, 0),
        'confirmados': por_status.get(Pedido.CONFIRMADO, 0),
        'em_preparo': por_status.get(Pedido.EM_PREPARO, 0),
        'concluidos': por_status.get(Pedido.ENTREGUE, 0),
    }

    filtro = request.GET.get('status', '')
    pedidos = Pedido.objects.select_related('cliente')
    if filtro in dict(Pedido.STATUS):
        pedidos = pedidos.filter(status=filtro)
    else:
        filtro = ''

    contexto = {
        'resumo': resumo,
        'pedidos': pedidos[:30],
        'filtro': filtro,
        'opcoes_status': Pedido.STATUS,
    }
    return render(request, 'pedidos/painel.html', contexto)


@funcionario_required
@require_POST
def alterar_status(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    novo_status = request.POST.get('status')

    if novo_status not in dict(Pedido.STATUS):
        messages.error(request, 'Status inválido.')
    else:
        pedido.status = novo_status
        pedido.save(update_fields=['status'])
        messages.success(
            request,
            f'Pedido {pedido.codigo} atualizado para "{pedido.get_status_display()}".',
        )

    return redirect('pedidos:detalhes', id=pedido.id)
