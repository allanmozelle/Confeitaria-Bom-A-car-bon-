from produtos.models import Produto


class Carrinho:
    """Carrinho de compras guardado na sessão do usuário: {id_do_produto: quantidade}."""

    CHAVE = 'carrinho'
    QUANTIDADE_MAXIMA = 50

    def __init__(self, request):
        self.session = request.session
        self.dados = self.session.get(self.CHAVE, {})

    def _salvar(self):
        self.session[self.CHAVE] = self.dados
        self.session.modified = True

    def adicionar(self, produto, quantidade=1):
        chave = str(produto.id)
        total = self.dados.get(chave, 0) + quantidade
        self.dados[chave] = max(1, min(total, self.QUANTIDADE_MAXIMA))
        self._salvar()

    def atualizar(self, produto_id, quantidade):
        chave = str(produto_id)
        if chave in self.dados:
            self.dados[chave] = max(1, min(quantidade, self.QUANTIDADE_MAXIMA))
            self._salvar()

    def remover(self, produto_id):
        if self.dados.pop(str(produto_id), None) is not None:
            self._salvar()

    def limpar(self):
        self.dados = {}
        self.session.pop(self.CHAVE, None)
        self.session.modified = True

    def itens(self):
        """Lista de dicionários: produto, quantidade, subtotal e disponível."""
        produtos = Produto.objects.select_related('categoria').in_bulk(
            [int(chave) for chave in self.dados]
        )
        itens = []
        for chave, quantidade in list(self.dados.items()):
            produto = produtos.get(int(chave))
            if produto is None:  # produto foi excluído do cardápio
                del self.dados[chave]
                self._salvar()
                continue
            itens.append({
                'produto': produto,
                'quantidade': quantidade,
                'subtotal': produto.preco * quantidade,
                'disponivel': produto.disponivel,
            })
        return itens

    def total(self, itens=None):
        itens = self.itens() if itens is None else itens
        return sum((i['subtotal'] for i in itens if i['disponivel']), 0)
