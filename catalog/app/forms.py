from django.forms import ModelForm

from .models import MyUser, Product


class LoginForm(ModelForm):
    class Meta:
        model = MyUser
        fields = ['username', 'password']


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'desc', 'amount']
