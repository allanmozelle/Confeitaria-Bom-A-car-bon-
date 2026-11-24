from django.urls import reverse

from django.test import TestCase

from .models import Usuario


class UsuarioModelTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='miguel',
            email='miguel@email.com',
            password='senha123',
            nome_completo='Miguel Oliveira',
        )

    def test_usuario_e_criado_como_cliente(self):
        self.assertEqual(self.usuario.tipo, Usuario.CLIENTE)

    def test_usuario_e_cliente(self):
        self.assertTrue(self.usuario.eh_cliente)
        self.assertFalse(self.usuario.eh_funcionario)

    def test_nome_completo(self):
        self.assertEqual(self.usuario.get_full_name(), 'Miguel Oliveira')

    def test_nome_curto(self):
        self.assertEqual(self.usuario.get_short_name(), 'Miguel')

    def test_superusuario_e_funcionario(self):
        superusuario = Usuario.objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='senha123',
            nome_completo='Administrador',
        )

        self.assertEqual(superusuario.tipo, Usuario.FUNCIONARIO)
        self.assertTrue(superusuario.eh_funcionario)

from .forms import CadastroForm


class CadastroFormTest(TestCase):

    def dados_validos(self):
        return {
            'nome_completo': 'João Silva',
            'email': 'joao@email.com',
            'username': 'joaosilva',
            'password1': 'SenhaForte123!',
            'password2': 'SenhaForte123!',
        }

    def test_cadastro_valido(self):
        form = CadastroForm(data=self.dados_validos())

        self.assertTrue(form.is_valid())

        usuario = form.save()

        self.assertEqual(usuario.tipo, Usuario.CLIENTE)
        self.assertEqual(usuario.email, 'joao@email.com')

    def test_email_duplicado(self):
        Usuario.objects.create_user(
            username='outro',
            email='joao@email.com',
            password='senha123',
            nome_completo='Outro Usuário',
        )

        form = CadastroForm(data=self.dados_validos())

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_username_duplicado(self):
        Usuario.objects.create_user(
            username='joaosilva',
            email='outro@email.com',
            password='senha123',
            nome_completo='Outro Usuário',
        )

        form = CadastroForm(data=self.dados_validos())

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class LoginTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='miguel',
            email='miguel@email.com',
            password='SenhaForte123!',
            nome_completo='Miguel Oliveira',
        )

    def test_login_com_username(self):
        resposta = self.client.post(
            reverse('usuarios:login'),
            {
                'username': 'miguel',
                'password': 'SenhaForte123!',
            },
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.wsgi_request.user.is_authenticated)

    def test_login_com_email(self):
        resposta = self.client.post(
            reverse('usuarios:login'),
            {
                'username': 'miguel@email.com',
                'password': 'SenhaForte123!',
            },
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.wsgi_request.user.is_authenticated)

    def test_login_com_senha_incorreta(self):
        resposta = self.client.post(
            reverse('usuarios:login'),
            {
                'username': 'miguel',
                'password': 'senhaerrada',
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(resposta.wsgi_request.user.is_authenticated)