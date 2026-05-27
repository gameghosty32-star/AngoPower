from django import forms

from utils.angola import PROVINCIAS, MUNICIPIOS, validate_angolan_phone


class CustomerOnboardingForm(forms.Form):
    phone = forms.CharField(
        label='Telefone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+244 9XX XXX XXX',
            'data-mask': '+244 999 999 999',
        }),
    )
    provincia = forms.ChoiceField(
        label='Província',
        choices=[('', '-- Seleccione --')] + [(p, p) for p in PROVINCIAS],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    municipio = forms.ChoiceField(
        label='Município',
        choices=[('', '-- Seleccione primeiro a província --')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    bairro = forms.CharField(
        label='Bairro',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do bairro'}),
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not validate_angolan_phone(phone):
            raise forms.ValidationError('Número de telefone angolano inválido. Formato: +244 9XX XXX XXX')
        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        provincia = self.data.get('provincia') if self.is_bound else self.initial.get('provincia', '')
        if provincia and provincia in MUNICIPIOS:
            self.fields['municipio'].choices = [('', '-- Seleccione --')] + [(m, m) for m in MUNICIPIOS[provincia]]
