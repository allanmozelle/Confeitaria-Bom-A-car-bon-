from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOuUsuarioBackend(ModelBackend):
    """Permite fazer login digitando o nome de usuário OU o e-mail."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        Usuario = get_user_model()

        if username is None:
            username = kwargs.get(Usuario.USERNAME_FIELD)
        if username is None or password is None:
            return None

        usuario = (
            Usuario.objects.filter(username__iexact=username).first()
            or Usuario.objects.filter(email__iexact=username).first()
        )

        if usuario is None:
            # Gasta o mesmo tempo de uma verificação real (evita descobrir
            # quais usuários existem pelo tempo de resposta).
            Usuario().set_password(password)
            return None

        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
