from django import forms
from .models import Feedback, Estados
from .choices import UNIDADES_POR_ESTADO

ESTADOS_CHOICES = [(estado.value, estado.label) for estado in Estados]

class FeedbackForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=ESTADOS_CHOICES, required=True, label="Estado")
    unidade_sus = forms.ChoiceField(choices=[], required=True, label="Unidade SUS")

    class Meta:
        model = Feedback
        fields = ['estado', 'unidade_sus', 'titulo', 'comentario']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'style': 'resize:none'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['estado'].widget.attrs.update({'class': 'form-select'})
        self.fields['unidade_sus'].widget.attrs.update({'class': 'form-select'})

        data = self.data or self.initial
        estado = data.get("estado")
        if estado in UNIDADES_POR_ESTADO:
            self.fields['unidade_sus'].choices = UNIDADES_POR_ESTADO[estado]
        else:
            self.fields['unidade_sus'].choices = [('', 'Selecione um estado primeiro')]
