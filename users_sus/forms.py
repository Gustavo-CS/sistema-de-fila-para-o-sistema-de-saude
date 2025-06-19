from django import forms
from .models import Feedback

UNIDADES_SUS_CHOICES = [
    ("Hospitais Regionais", [
        ("HBDF", "Hospital de Base do DF (HBDF)"),
        ("HRAN", "Hospital Regional da Asa Norte (HRAN)"),
        ("HRAS", "Hospital Regional da Asa Sul (HRAS)"),
        ("HRC", "Hospital Regional de Ceilândia (HRC)"),
        ("HRT", "Hospital Regional de Taguatinga (HRT)"),
        ("HRSam", "Hospital Regional de Samambaia (HRSam)"),
        ("HRG", "Hospital Regional do Gama (HRG)"),
        ("HRBz", "Hospital Regional de Brazlândia (HRBz)"),
        ("HRP", "Hospital Regional de Planaltina (HRP)"),
        ("HRS", "Hospital Regional de Sobradinho (HRS)"),
        ("HUB", "Hospital Universitário de Brasília (HUB)"),
        ("HMIB", "Hospital Materno Infantil de Brasília (HMIB)"),
    ]),
    ("Unidades Básicas de Saúde (UBS)", [
        ("UBS1Ceilandia", "UBS 1 de Ceilândia"),
        ("UBS2Ceilandia", "UBS 2 de Ceilândia"),
        ("UBS1Taguatinga", "UBS 1 de Taguatinga"),
        ("UBS2Taguatinga", "UBS 2 de Taguatinga"),
        ("UBS1Samambaia", "UBS 1 de Samambaia"),
        ("UBS2Samambaia", "UBS 2 de Samambaia"),
        ("UBS1Gama", "UBS 1 do Gama"),
        ("UBS1Brazlandia", "UBS 1 de Brazlândia"),
        ("UBS1Planaltina", "UBS 1 de Planaltina"),
        ("UBS1Sobradinho", "UBS 1 de Sobradinho"),
        ("UBS1Paranoa", "UBS 1 do Paranoá"),
        ("UBS1Recanto", "UBS 1 do Recanto das Emas"),
        ("UBS1Sebastiao", "UBS 1 de São Sebastião"),
        ("UBS1RiachoI", "UBS 1 do Riacho Fundo I"),
        ("UBS1RiachoII", "UBS 1 do Riacho Fundo II"),
        ("UBS1Nucleo", "UBS 1 do Núcleo Bandeirante"),
    ]),
    ("Outros Serviços", [
        ("CTA", "CTA da Rodoviária do Plano Piloto"),
        ("CAPS", "CAPS de Ceilândia"),
        ("FarmaciaGama", "Farmácia de Alto Custo do Gama"),
        ("LACEN", "Laboratório Central (LACEN)"),
    ]),
]

class FeedbackForm(forms.Form):
    unidade_sus = forms.ChoiceField(
        label="Unidade SUS",
        choices=UNIDADES_SUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    titulo = forms.CharField(
        label="Título",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite um título',
            'class': 'form-control'
        })
    )
    comentario = forms.CharField(
        label="Comentário",
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Digite seu feedback aqui',
            'rows': 5,
            'style': 'resize: none;',
            'class': 'form-control'
        })
    )