from django import forms

from .models import Categoria, Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'descricao', 'preco', 'imagem', 'disponivel']
        labels = {
            'nome': 'Nome do produto',
            'preco': 'Preço',
            'imagem': 'Imagem do produto',
            'disponivel': 'Produto disponível para pedidos',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Bolo de Chocolate'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Descreva o produto...'}),
            'preco': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': 'Ex.: 45.00'}),
            'imagem': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = 'Selecione uma categoria'


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        labels = {
            'nome': 'Nome da categoria',
            'descricao': 'Descrição (opcional)',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Bolos'}),
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }
