from datetime import datetime, timezone, timedelta
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
from .models import MyUser, Product, Order, CancelledOrder


# Create your views here.

class LogView(LoginView):
    template_name = 'log.html'
    success_url = '/products'

    def get_success_url(self):
        return self.success_url

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
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
                ord = Order.objects.create(owner=user, position=product, quantity=user_amount)
                ord.save()
                product.save()
                user.save()
        return HttpResponseRedirect("/products")

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(name='products', **kwargs)


class OrderViewList(LoginRequiredMixin, ListView):
    login_url = "/login"
    model = Order
    template_name = 'orders.html'
    paginate_by = 5
    ordering = ['order_date']

    def get_queryset(self):
        queryset = Order.objects.filter(owner__id=self.request.user.id)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
        queryset = queryset.order_by(*ordering)
        return queryset

    '''def get_context_data(self, *, object_list=None, **kwargs):
        res = [x.quantity * x.position.price for x in
               Order.objects.order_by('order_date').filter(owner__id=self.request.user.id)]
        return super().get_context_data(price=res, **kwargs)'''

    def post(self, request, *args, **kwargs):
        order = Order.objects.filter(id=request.POST['id']).first()
        if datetime.now(timezone.utc) - order.order_date <= timedelta(minutes=3):
            cancelled_order = CancelledOrder.objects.create(cancel=order)
            order.discarded = True
            order.save()
            cancelled_order.save()
        return HttpResponseRedirect("/orders")


class DiscardedOrdersViewList(PermissionRequiredMixin, ListView):
    permission_required = 'request.user.is_superuser'
    model = CancelledOrder
    fields = '__all__'
    template_name = 'cancelled.html'
    paginate_by = 5

    def post(self, request, *args, **kwargs):
        post_id = request.POST['id']
        usr_id = CancelledOrder.objects.filter(id=post_id).first().cancel.owner.id
        usr = MyUser.objects.filter(id=usr_id).first()
        price = CancelledOrder.objects.filter(id=post_id).first().cancel.position.price
        amount = CancelledOrder.objects.filter(id=post_id).first().cancel.quantity
        usr.balance += amount*price
        usr.save()
        product = CancelledOrder.objects.filter(id=post_id).first().cancel.position
        product.amount += amount
        product.save()
        CancelledOrder.objects.filter(id=post_id).first().cancel.delete()
        return HttpResponseRedirect('/cancelled')


    '''def get_context_data(self, *, object_list=None, **kwargs):
        res = []
        for usr in MyUser.objects.all():
            res += [x.cancel.quantity * x.cancel.position.price for x in
                CancelledOrder.objects.order_by('cancel_date').filter(cancel__owner__id=usr.id)]
        return super().get_context_data(price=res, **kwargs)'''

class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'request.user.is_superuser'
    model = Product
    fields = '__all__'
    template_name = 'change_product.html'
    success_url = "/products"


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
