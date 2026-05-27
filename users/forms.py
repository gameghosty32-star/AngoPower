from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    customer_type = forms.ChoiceField(
        label='Tipo de Conta',
        choices=[('prepaid', 'Pré-pago'), ('postpaid', 'Pós-pago')],
        widget=forms.RadioSelect,
        initial='prepaid',
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'customer_type':
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[field_name].label or field_name,
                })
