from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView, FormView, UpdateView, RedirectView
from django.core.cache import cache
import random

from .forms import LoginForm, ProductForm, RegForm
from .models import MyUser, Product


# Create your views here.

class LogView(LoginView):
    template_name = 'log.html'
    success_url = '/products'

    def get_success_url(self):
        return self.success_url

    def get(self, *args, **kwargs):
        if self.request.user.username:
            return HttpResponseRedirect('/products')
        return super().get(request=self.request)


class RegistrateView(FormView):
    form_class = RegForm
    template_name = 'log.html'
    success_url = '/products'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            username = form.cleaned_data['name']
            password = form.cleaned_data['password']
            MyUser.objects.create_user(username=username, email=None, password=password)
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/products')
        else:
            form.errors.update({'passes': 'passwords do not match'})
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        if self.request.user.username:
            return HttpResponseRedirect('/products')
        else:
            return super().get(request=request, *args, **kwargs)


class OutView(LogoutView):
    login_url = '/products'
    template_name = 'index.html'
    next_page = '/products'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    success_url = '/product'
    template_name = 'index.html'


class ProductViewList(ListView):
    model = Product
    queryset = Product.objects.all()
    template_name = 'products.html'
    form_class = ProductForm
    paginate_by = 3
    ordering = ['price']

    def post(self, request, *args, **kwargs):
        user_amount = int(request.POST['amount'])
        product_id = request.POST['id']
        product = Product.objects.filter(id=product_id).first()
        if user_amount <= product.amount:
            user_id = request.user.id
            user = MyUser.objects.filter(id=user_id).first()
            if user.balance - (product.price * user_amount) >= 0:
                user.balance -= product.price * user_amount
                product.amount -= user_amount
                product.save()
                user.save()
        return HttpResponseRedirect("/products")

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(name='products', **kwargs)


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'request.user.is_superuser'
    model = Product
    fields = '__all__'
    template_name = 'change_product.html'


class MainRedirectView(RedirectView):
    url = "/products/"


class GameView(TemplateView):
    template_name = 'game.html'

    def get_context_data(self, **kwargs):
        if 'score' in self.request.session.keys():
            tmp = self.request.session['score']
            if tmp > 10:
                res = "you lose" if tmp % 2 else "you win"

            else:
                self.request.session['score'] += random.randint(3, 8)
                res = None
        else:
            self.request.session['score'] = 0
            tmp = 0
            res = None
        return super(GameView, self).get_context_data(score=tmp, res=res, **kwargs)


class CounterView(TemplateView):
    template_name = 'cache.html'

    def get_context_data(self, **kwargs):
        if cache.get('count'):
            tmp = cache.get('count')
            tmp += 1
            cache.set('count', tmp)
        else:
            cache.set('count', 1)
        tmp_users = cache.get("users") if cache.get("users") else set()
        tmp_users.add(self.request.user)
        cache.set('users', tmp_users)
        return super().get_context_data(count=cache.get('count'), users=cache.get('users'), **kwargs)
