from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Representa clientes e funcionários da confeitaria."""

    CLIENTE = 'cliente'
    FUNCIONARIO = 'funcionario'
    TIPOS = [
        (CLIENTE, 'Cliente'),
        (FUNCIONARIO, 'Funcionário'),
    ]

    nome_completo = models.CharField('nome completo', max_length=150)
    email = models.EmailField('e-mail', unique=True)
    tipo = models.CharField(
        'tipo de usuário',
        max_length=12,
        choices=TIPOS,
        default=CLIENTE,
    )

    # Campos pedidos ao criar um superusuário pelo terminal.
    REQUIRED_FIELDS = ['email', 'nome_completo']

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def save(self, *args, **kwargs):
        # Quem é superusuário (createsuperuser) sempre é funcionário.
        if self.is_superuser:
            self.tipo = self.FUNCIONARIO
        super().save(*args, **kwargs)

    @property
    def eh_funcionario(self):
        return self.tipo == self.FUNCIONARIO

    @property
    def eh_cliente(self):
        return self.tipo == self.CLIENTE

    def get_full_name(self):
        return self.nome_completo or self.username

    def get_short_name(self):
        return (self.nome_completo or self.username).split(' ')[0]

    def __str__(self):
        return self.nome_completo or self.username
