from django.contrib import admin

from .models import ItemPedido, Pedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('produto', 'nome_produto', 'quantidade', 'preco_unitario')
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'cliente', 'data', 'status', 'valor_total')
    list_filter = ('status',)
    search_fields = ('codigo', 'cliente__nome_completo', 'cliente__username')
    readonly_fields = ('codigo', 'data', 'valor_total')
    inlines = [ItemPedidoInline]
