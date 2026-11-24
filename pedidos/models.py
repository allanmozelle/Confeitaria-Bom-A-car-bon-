import secrets
import string
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Pedido(models.Model):
    PENDENTE = 'pendente'
    CONFIRMADO = 'confirmado'
    EM_PREPARO = 'em_preparo'
    PRONTO = 'pronto'
    ENTREGUE = 'entregue'
    CANCELADO = 'cancelado'

    STATUS = [
        (PENDENTE, 'Pendente'),
        (CONFIRMADO, 'Confirmado'),
        (EM_PREPARO, 'Em preparo'),
        (PRONTO, 'Pronto'),
        (ENTREGUE, 'Entregue'),
        (CANCELADO, 'Cancelado'),
    ]

    codigo = models.CharField(max_length=12, unique=True, editable=False)
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos',
    )
    data = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS, default=PENDENTE)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    telefone = models.CharField(max_length=20)
    endereco = models.CharField('endereço', max_length=200)
    observacoes = models.TextField('observações', blank=True)

    class Meta:
        ordering = ['-data']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._gerar_codigo()
        super().save(*args, **kwargs)

    @staticmethod
    def _gerar_codigo():
        """Gera um código único, ex.: BA-7F3K9Q."""
        alfabeto = string.ascii_uppercase + string.digits
        while True:
            codigo = 'BA-' + ''.join(secrets.choice(alfabeto) for _ in range(6))
            if not Pedido.objects.filter(codigo=codigo).exists():
                return codigo

    @property
    def classe_status(self):
        """Nome da classe CSS do status (ex.: em_preparo -> em-preparo)."""
        return self.status.replace('_', '-')

    def __str__(self):
        return f'Pedido {self.codigo}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    # SET_NULL: se o produto for excluído do cardápio, o histórico do pedido continua.
    produto = models.ForeignKey(
        'produtos.Produto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_pedido',
    )
    nome_produto = models.CharField(max_length=100)  # nome no momento da compra
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField('preço unitário', max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'item do pedido'
        verbose_name_plural = 'itens do pedido'

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f'{self.nome_produto} × {self.quantidade}'
