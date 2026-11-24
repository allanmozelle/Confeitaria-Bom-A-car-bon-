from django.test import Client

from django.urls import reverse

from .forms import FinalizarPedidoForm

from decimal import Decimal

from django.test import TestCase

from usuarios.models import Usuario
from produtos.models import Categoria, Produto

from .models import Pedido, ItemPedido


class PedidoModelTest(TestCase):

    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            email='cliente@email.com',
            password='senha123',
            nome_completo='Cliente Teste',
        )

        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            telefone='82999999999',
            endereco='Rua das Flores, 100',
            valor_total=Decimal('50.00'),
        )

    def test_pedido_recebe_codigo_automaticamente(self):
        self.assertTrue(self.pedido.codigo.startswith('BA-'))
        self.assertEqual(len(self.pedido.codigo), 9)

    def test_status_inicial_pendente(self):
        self.assertEqual(self.pedido.status, Pedido.PENDENTE)

    def test_codigo_e_unico(self):
        outro_pedido = Pedido.objects.create(
            cliente=self.cliente,
            telefone='82999999999',
            endereco='Rua das Flores, 100',
        )

        self.assertNotEqual(self.pedido.codigo, outro_pedido.codigo)

    def test_classe_status(self):
        self.pedido.status = Pedido.EM_PREPARO

        self.assertEqual(self.pedido.classe_status, 'em-preparo')


class ItemPedidoModelTest(TestCase):

    def setUp(self):
        cliente = Usuario.objects.create_user(
            username='cliente',
            email='cliente@email.com',
            password='senha123',
            nome_completo='Cliente Teste',
        )

        pedido = Pedido.objects.create(
            cliente=cliente,
            telefone='82999999999',
            endereco='Rua das Flores, 100',
        )

        self.item = ItemPedido.objects.create(
            pedido=pedido,
            nome_produto='Bolo de Chocolate',
            quantidade=2,
            preco_unitario=Decimal('25.00'),
        )

    def test_subtotal(self):
        self.assertEqual(self.item.subtotal, Decimal('50.00'))

    def test_representacao_item(self):
        self.assertEqual(str(self.item), 'Bolo de Chocolate × 2')

class FinalizarPedidoFormTest(TestCase):

    def dados_validos(self):
        return {
            'telefone': '(82) 99999-9999',
            'endereco': 'Rua das Flores, 100',
            'observacoes': 'Entregar à tarde',
        }

    def test_formulario_valido(self):
        form = FinalizarPedidoForm(data=self.dados_validos())

        self.assertTrue(form.is_valid())

    def test_telefone_invalido(self):
        dados = self.dados_validos()
        dados['telefone'] = '12345'

        form = FinalizarPedidoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn('telefone', form.errors)

    def test_telefone_com_ddd_valido(self):
        dados = self.dados_validos()
        dados['telefone'] = '82999999999'

        form = FinalizarPedidoForm(data=dados)

        self.assertTrue(form.is_valid())

class CarrinhoViewsTest(TestCase):

    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            email='cliente@email.com',
            password='senha123',
            nome_completo='Cliente Teste',
        )

        self.categoria = Categoria.objects.create(nome='Bolos')

        self.produto = Produto.objects.create(
            nome='Bolo de Chocolate',
            descricao='Bolo tradicional',
            preco=Decimal('45.00'),
            categoria=self.categoria,
        )

        self.client.force_login(self.cliente)

    def test_adicionar_produto_ao_carrinho(self):
        resposta = self.client.post(
            reverse('pedidos:adicionar_carrinho', args=[self.produto.id]),
            {'quantidade': 2},
        )

        carrinho = self.client.session['carrinho']

        self.assertEqual(carrinho[str(self.produto.id)], 2)
        self.assertRedirects(resposta, reverse('pedidos:carrinho'))

    def test_quantidade_maxima_no_carrinho(self):
        self.client.post(
            reverse('pedidos:adicionar_carrinho', args=[self.produto.id]),
            {'quantidade': 60},
        )

        carrinho = self.client.session['carrinho']

        self.assertEqual(carrinho[str(self.produto.id)], 50)

    def test_atualizar_quantidade(self):
        self.client.post(
            reverse('pedidos:adicionar_carrinho', args=[self.produto.id]),
            {'quantidade': 2},
        )

        self.client.post(
            reverse('pedidos:atualizar_carrinho', args=[self.produto.id]),
            {'quantidade': 5},
        )

        carrinho = self.client.session['carrinho']

        self.assertEqual(carrinho[str(self.produto.id)], 5)

    def test_remover_produto(self):
        self.client.post(
            reverse('pedidos:adicionar_carrinho', args=[self.produto.id]),
            {'quantidade': 2},
        )

        self.client.post(
            reverse('pedidos:remover_carrinho', args=[self.produto.id])
        )

        carrinho = self.client.session.get('carrinho', {})

        self.assertNotIn(str(self.produto.id), carrinho)

    def test_finalizar_com_carrinho_vazio(self):
        resposta = self.client.get(reverse('pedidos:finalizar'))

        self.assertRedirects(
            resposta,
            reverse('pedidos:carrinho')
        )

        self.assertEqual(Pedido.objects.count(), 0)

    def test_finalizar_pedido_com_sucesso(self):
        self.client.post(
            reverse('pedidos:adicionar_carrinho', args=[self.produto.id]),
            {'quantidade': 2},
        )

        resposta = self.client.post(
            reverse('pedidos:finalizar'),
            {
                'telefone': '82999999999',
                'endereco': 'Rua de teste, 123',
                'observacoes': 'Sem observações',
            },
        )

        pedido = Pedido.objects.get()

        self.assertRedirects(
            resposta,
            reverse('pedidos:detalhes', args=[pedido.id])
        )

        self.assertEqual(pedido.cliente, self.cliente)
        self.assertEqual(pedido.valor_total, Decimal('90.00'))
        self.assertEqual(pedido.itens.count(), 1)
        self.assertEqual(pedido.itens.first().quantidade, 2)
        self.assertNotIn('carrinho', self.client.session)

    def test_total_do_pedido_e_calculado_no_servidor(self):
        self.client.post(
            reverse('pedidos:adicionar_carrinho', args=[self.produto.id]),
            {'quantidade': 2},
        )

        self.client.post(
            reverse('pedidos:finalizar'),
            {
                'telefone': '82999999999',
                'endereco': 'Rua de teste, 123',
                'observacoes': '',
                'valor_total': '0.01',
            },
        )

        pedido = Pedido.objects.get()

        self.assertEqual(pedido.valor_total, Decimal('90.00'))

class DetalhesPedidoViewsTest(TestCase):

    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            email='cliente@email.com',
            password='senha123',
            nome_completo='Cliente Teste',
        )

        self.outro_cliente = Usuario.objects.create_user(
            username='outro',
            email='outro@email.com',
            password='senha123',
            nome_completo='Outro Cliente',
        )

        self.funcionario = Usuario.objects.create_user(
            username='funcionario',
            email='funcionario@email.com',
            password='senha123',
            nome_completo='Funcionário Teste',
            tipo=Usuario.FUNCIONARIO,
        )

        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            telefone='82999999999',
            endereco='Rua de Teste, 123',
            valor_total=Decimal('45.00'),
        )

    def test_visitante_e_redirecionado_para_login(self):
        resposta = self.client.get(
            reverse('pedidos:detalhes', args=[self.pedido.id])
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/login/', resposta.url)

    def test_cliente_visualiza_proprio_pedido(self):
        self.client.force_login(self.cliente)

        resposta = self.client.get(
            reverse('pedidos:detalhes', args=[self.pedido.id])
        )

        self.assertEqual(resposta.status_code, 200)

    def test_cliente_nao_visualiza_pedido_de_outro(self):
        self.client.force_login(self.outro_cliente)

        resposta = self.client.get(
            reverse('pedidos:detalhes', args=[self.pedido.id])
        )

        self.assertEqual(resposta.status_code, 404)

    def test_funcionario_visualiza_pedido_de_qualquer_cliente(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.get(
            reverse('pedidos:detalhes', args=[self.pedido.id])
        )

        self.assertEqual(resposta.status_code, 200)

class ProtecaoCSRFTest(TestCase):

    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            password='senha123',
            nome_completo='Cliente Teste',
            email='cliente@teste.com'
        )

        self.produto = Produto.objects.create(
            nome='Bolo de chocolate',
            descricao='Bolo de teste',
            preco=Decimal('30.00'),
            categoria=Categoria.objects.create(nome='Bolos')
        )

        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.cliente)

    def test_adicionar_carrinho_sem_token_csrf(self):
        resposta = self.client.post(
            reverse('pedidos:adicionar_carrinho', args=[self.produto.id]),
            {'quantidade': 1}
        )

        self.assertEqual(resposta.status_code, 403)

class AlterarStatusPedidoTest(TestCase):

    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            password='senha123',
            nome_completo='Cliente Teste',
            email='cliente@email.com',
        )

        self.funcionario = Usuario.objects.create_user(
            username='funcionario',
            password='senha123',
            nome_completo='Funcionario Teste',
            email='funcionario@email.com',
            tipo=Usuario.FUNCIONARIO,
        )

        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            telefone='82999999999',
            endereco='Rua de Teste, 123',
            valor_total=Decimal('45.00'),
        )

    def test_funcionario_altera_status(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.post(
            reverse('pedidos:alterar_status', args=[self.pedido.id]),
            {'status': Pedido.CONFIRMADO},
        )

        self.pedido.refresh_from_db()

        self.assertEqual(self.pedido.status, Pedido.CONFIRMADO)
        self.assertRedirects(
            resposta,
            reverse('pedidos:detalhes', args=[self.pedido.id])
        )

    def test_cliente_nao_altera_status(self):
        self.client.force_login(self.cliente)

        resposta = self.client.post(
            reverse('pedidos:alterar_status', args=[self.pedido.id]),
            {'status': Pedido.CONFIRMADO},
        )

        self.pedido.refresh_from_db()

        self.assertNotEqual(self.pedido.status, Pedido.CONFIRMADO)
        self.assertRedirects(resposta, reverse('principal:home'))

    def test_get_nao_altera_status(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.get(
            reverse('pedidos:alterar_status', args=[self.pedido.id])
        )

        self.pedido.refresh_from_db()

        self.assertEqual(resposta.status_code, 405)
        self.assertEqual(self.pedido.status, Pedido.PENDENTE)

    def test_status_invalido_nao_altera_pedido(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.post(
            reverse('pedidos:alterar_status', args=[self.pedido.id]),
            {'status': 'status_inexistente'},
        )

        self.pedido.refresh_from_db()

        self.assertEqual(self.pedido.status, Pedido.PENDENTE)
        self.assertRedirects(
            resposta,
            reverse('pedidos:detalhes', args=[self.pedido.id])
        )