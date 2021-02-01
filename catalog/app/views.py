from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView
from django.core.cache import cache
import random

from .forms import LoginForm, ProductForm
from .models import MyUser, Product


# Create your views here.

class LogView(LoginView):
    template_name = 'log.html'
    success_url = '/thanks'

    def get_success_url(self):
        return self.success_url

    def get(self, *args, **kwargs):
        if self.request.user.username:
            return HttpResponseRedirect('/main')
        return super().get(request=self.request)


class OutView(LogoutView):
    login_url = '/login'
    x = 5
    template_name = 'index.html'
    next_page = '/main'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    success_url = '/thanks'
    template_name = 'index.html'


class ProductViewList(ListView):
    model = Product
    queryset = Product.objects.all()
    template_name = 'products.html'


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
        tmp_users = cache.get("users") if cache.get("users") else {}
        tmp_users.append(self.request.user)
        cache.set('users', tmp_users)
        return super().get_context_data(count=cache.get('count'), users=cache.get('users'), **kwargs)
