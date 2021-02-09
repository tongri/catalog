from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms

from .models import Product, Order, MyUser, CancelledOrder


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
        exclude = '__all__'

    def is_valid(self):
        return super().is_valid()


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def is_valid(self):
        self.data = self.data.copy()
        self.data['position'] = Product.objects.get(id=self.data['position'])
        self.data['owner'] = MyUser.objects.get(id=self.data['owner'])
        return super().is_valid()


class DiscardForm(ModelForm):
    class Meta:
        model = CancelledOrder
        fields = '__all__'

    def is_valid(self):
        self.data = self.data.copy()
        self.data['cancel'] = Order.objects.get(id=self.data['cancel'])
        return super().is_valid()
