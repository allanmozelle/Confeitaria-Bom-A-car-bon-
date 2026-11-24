from django.urls import reverse

from usuarios.models import Usuario

from .forms import CategoriaForm, ProdutoForm

from decimal import Decimal

from django.test import TestCase

from .models import Categoria, Produto


class CategoriaModelTest(TestCase):

    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome='Bolos',
            descricao='Bolos variados',
        )

    def test_categoria_e_criada(self):
        self.assertEqual(self.categoria.nome, 'Bolos')

    def test_representacao_categoria(self):
        self.assertEqual(str(self.categoria), 'Bolos')


class ProdutoModelTest(TestCase):

    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Bolos')

        self.produto = Produto.objects.create(
            nome='Bolo de Chocolate',
            descricao='Bolo de chocolate tradicional',
            preco=Decimal('45.00'),
            categoria=self.categoria,
        )

    def test_produto_e_criado_disponivel(self):
        self.assertTrue(self.produto.disponivel)

    def test_produto_pertence_a_categoria(self):
        self.assertEqual(self.produto.categoria, self.categoria)

    def test_representacao_produto(self):
        self.assertEqual(str(self.produto), 'Bolo de Chocolate')

    def test_categoria_nao_pode_ser_excluida_com_produtos(self):
        from django.db.models import ProtectedError

        with self.assertRaises(ProtectedError):
            self.categoria.delete()

class CategoriaFormTest(TestCase):

    def test_categoria_valida(self):
        form = CategoriaForm(data={
            'nome': 'Doces',
            'descricao': 'Doces variados',
        })

        self.assertTrue(form.is_valid())

    def test_categoria_sem_nome(self):
        form = CategoriaForm(data={
            'nome': '',
            'descricao': 'Doces variados',
        })

        self.assertFalse(form.is_valid())


class ProdutoFormTest(TestCase):

    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Bolos')

    def dados_validos(self):
        return {
            'nome': 'Bolo de Chocolate',
            'categoria': self.categoria.id,
            'descricao': 'Bolo de chocolate tradicional',
            'preco': '45.00',
            'disponivel': True,
        }

    def test_produto_valido(self):
        form = ProdutoForm(data=self.dados_validos())

        self.assertTrue(form.is_valid())

    def test_produto_com_preco_zero(self):
        dados = self.dados_validos()
        dados['preco'] = '0.00'

        form = ProdutoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn('preco', form.errors)

    def test_produto_sem_categoria(self):
        dados = self.dados_validos()
        dados['categoria'] = ''

        form = ProdutoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn('categoria', form.errors)

class ProdutoViewsTest(TestCase):

    def setUp(self):
        self.funcionario = Usuario.objects.create_user(
            username='funcionario',
            email='funcionario@email.com',
            password='senha123',
            nome_completo='Funcionário',
            tipo=Usuario.FUNCIONARIO,
        )

        self.cliente = Usuario.objects.create_user(
            username='cliente',
            email='cliente@email.com',
            password='senha123',
            nome_completo='Cliente',
        )

        self.categoria = Categoria.objects.create(nome='Bolos')

    def dados_produto(self):
        return {
            'nome': 'Bolo de Chocolate',
            'categoria': self.categoria.id,
            'descricao': 'Bolo tradicional',
            'preco': '45.00',
            'disponivel': True,
        }

    def test_funcionario_acessa_cadastro(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.get(reverse('produtos:cadastrar'))

        self.assertEqual(resposta.status_code, 200)

    def test_cliente_nao_acessa_cadastro(self):
        self.client.force_login(self.cliente)

        resposta = self.client.get(reverse('produtos:cadastrar'))

        self.assertRedirects(resposta, reverse('principal:home'))

    def test_funcionario_cadastra_produto(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.post(
            reverse('produtos:cadastrar'),
            self.dados_produto(),
        )

        self.assertEqual(Produto.objects.count(), 1)
        self.assertRedirects(resposta, reverse('produtos:cardapio'))

    def test_exclusao_exige_post(self):
        produto = Produto.objects.create(
            nome='Bolo',
            descricao='Bolo simples',
            preco=Decimal('30.00'),
            categoria=self.categoria,
        )

    def test_funcionario_edita_produto(self):
        produto = Produto.objects.create(
            nome='Bolo',
            descricao='Bolo simples',
            preco=Decimal('30.00'),
            categoria=self.categoria,
        )

        self.client.force_login(self.funcionario)

        dados = self.dados_produto()
        dados['nome'] = 'Bolo Atualizado'

        resposta = self.client.post(
            reverse('produtos:editar', args=[produto.id]),
            dados,
        )

        produto.refresh_from_db()

        self.assertEqual(produto.nome, 'Bolo Atualizado')
        self.assertRedirects(resposta, reverse('produtos:cardapio'))

    def test_alternar_disponibilidade(self):
        produto = Produto.objects.create(
            nome='Bolo',
            descricao='Bolo simples',
            preco=Decimal('30.00'),
            categoria=self.categoria,
        )

        self.client.force_login(self.funcionario)

        resposta = self.client.post(
            reverse('produtos:disponibilidade', args=[produto.id])
        )

        produto.refresh_from_db()

        self.assertFalse(produto.disponivel)
        self.assertRedirects(resposta, reverse('produtos:cardapio'))

    def test_funcionario_cadastra_categoria(self):
        self.client.force_login(self.funcionario)

        resposta = self.client.post(
            reverse('produtos:categorias'),
            {
                'nome': 'Doces',
                'descricao': 'Doces variados',
            },
        )

        self.assertTrue(Categoria.objects.filter(nome='Doces').exists())
        self.assertRedirects(resposta, reverse('produtos:categorias'))

    def test_exclusao_categoria_com_produtos_e_bloqueada(self):
        produto = Produto.objects.create(
            nome='Bolo',
            descricao='Bolo simples',
            preco=Decimal('30.00'),
            categoria=self.categoria,
        )

        self.client.force_login(self.funcionario)

        resposta = self.client.post(
            reverse('produtos:excluir_categoria', args=[self.categoria.id])
        )

        self.assertTrue(Categoria.objects.filter(id=self.categoria.id).exists())
        self.assertRedirects(resposta, reverse('produtos:categorias'))

        self.client.force_login(self.funcionario)

        resposta = self.client.get(
            reverse('produtos:excluir', args=[produto.id])
        )

        self.assertEqual(resposta.status_code, 405)
        self.assertTrue(Produto.objects.filter(id=produto.id).exists())