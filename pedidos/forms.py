import re

from django import forms

from .models import Pedido


class FinalizarPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['telefone', 'endereco', 'observacoes']
        labels = {
            'telefone': 'Telefone',
            'endereco': 'Endereço',
            'observacoes': 'Observações',
        }
        widgets = {
            'telefone': forms.TextInput(attrs={'type': 'tel', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, número e bairro'}),
            'observacoes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Alguma informação adicional?'}),
        }

    def clean_telefone(self):
        telefone = self.cleaned_data['telefone'].strip()
        digitos = re.sub(r'\D', '', telefone)
        if not 10 <= len(digitos) <= 13:
            raise forms.ValidationError('Informe um telefone válido com DDD.')
        return telefone
