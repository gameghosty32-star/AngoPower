from django import forms


class InspectionRequestForm(forms.Form):
    inspection_notes = forms.CharField(
        label='Observações para a Vistoria',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Informe detalhes relevantes para a vistoria...',
        }),
    )


APPLIANCE_CHOICES = [
    ('fridge', 'Frigorífico - 5.000 Kz'),
    ('ac', 'Ar Condicionado - 8.000 Kz'),
    ('tv', 'Televisão - 2.000 Kz'),
    ('microwave', 'Micro-ondas - 3.000 Kz'),
    ('washing_machine', 'Máquina de Lavar - 4.000 Kz'),
]


class SystemSuggestionForm(forms.Form):
    appliances = forms.MultipleChoiceField(
        label='Seleccione os electrodomésticos',
        choices=APPLIANCE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    is_commercial = forms.BooleanField(
        label='Espaço comercial (aplica multiplicador 1.5x)',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
