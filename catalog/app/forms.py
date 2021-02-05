from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms

from .models import Product, Order


class RegForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput)
    confirm = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput)

    def clean_confirm(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('confirm'):
            raise ValidationError("passwords didnt match")


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'desc', 'amount', 'price', 'photo']
