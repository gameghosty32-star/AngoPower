from django import forms

from .services import get_active_gateways


class GatewaySelectionForm(forms.Form):
    gateway = forms.ChoiceField(
        label='Método de Pagamento',
        widget=forms.RadioSelect(attrs={'class': 'gateway-radio'}),
    )
    phone = forms.CharField(
        label='Número de Telefone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+244 9XX XXX XXX',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gateways = get_active_gateways()
        choices = [(g.code, g.name) for g in gateways]
        self.fields['gateway'].choices = choices
