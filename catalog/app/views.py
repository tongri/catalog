from datetime import datetime, timezone, timedelta
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, FormView, UpdateView, RedirectView, DeleteView
from .forms import ProductForm, RegForm, OrderForm, DiscardForm
from .models import MyUser, Product, Order, CancelledOrder


# Create your views here.


class LogView(LoginView):
    template_name = 'log.html'
    success_url = '/products'

    def get_success_url(self):
        return self.success_url

    def get(self, *args, **kwargs):  # Redirect to main page if authenticated
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/products')
        return super().get(request=self.request)


class RegistrateView(FormView):
    form_class = RegForm
    template_name = 'log.html'
    success_url = '/products'

    def form_valid(self, form):  # Create new user and log him in
        username = form.cleaned_data['name']
        password = form.cleaned_data['password']
        MyUser.objects.create_user(username=username, email=None, password=password)
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):  # Redirect to main page if authenticated
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/products')
        else:
            return super().get(request=request, *args, **kwargs)


class OutView(LogoutView):  # view for logging user out
    login_url = '/products'
    template_name = 'index.html'
    next_page = '/products'


class ProductCreateView(PermissionRequiredMixin, CreateView):  # view for creating products by admin
    login_url = '/login'
    permission_required = 'request.user.is_superuser'
    model = Product
    form_class = ProductForm
    success_url = '/products/'
    template_name = 'index.html'


class ProductViewList(ListView):  # view to show all products
    model = Product
    template_name = 'products.html'
    paginate_by = 3
    http_method_names = ['get', 'post']
    ordering = ['-amount', 'price']
    extra_context = {'name': 'products'}


class OrderCreateView(CreateView):  # view to buy a product
    model = Order
    form_class = OrderForm
    success_url = '/products/'

    def get(self, request, *args, **kwargs):  # if user tries to get by url
        return HttpResponseRedirect(reverse('products'))

    def form_valid(self, form):
        user_amount = int(form.cleaned_data.get('quantity'))
        if user_amount <= 0:
            messages.error(self.request, 'Sorry, wrong number of product to buy')
            return HttpResponseRedirect(self.success_url)
        product = form.cleaned_data.get('position')
        product.amount = int(product.amount)
        if user_amount <= product.amount:  # check if there is enough products to buy
            user = form.cleaned_data.get('owner')
            if user.balance - (product.price * user_amount) >= 0:  # check if user has enough money
                user.balance -= product.price * user_amount
                product.amount -= user_amount
                ord = Order.objects.create(owner=user, position=product, quantity=user_amount)
                ord.save()
                product.save()
                user.save()
                messages.info(self.request, 'Thnx 4 order')
            else:
                messages.error(self.request, 'Sorry, u dont have enough money')
        else:
            messages.error(self.request, 'Sorry, wrong number of product to buy')
        return HttpResponseRedirect(self.success_url)


class OrderViewList(LoginRequiredMixin, ListView):  # view to show user's orders
    login_url = "/login"
    model = Order
    template_name = 'orders.html'
    paginate_by = 5
    ordering = ['-order_date']

    def get_queryset(self):  # get queryset for exact user
        queryset = Order.objects.filter(owner__id=self.request.user.id)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
        queryset = queryset.order_by(*ordering)
        return queryset


class OrderDiscardView(LoginRequiredMixin, CreateView):  # view to cancel order
    model = CancelledOrder
    form_class = DiscardForm
    login_url = '/login/'

    def get(self):  # if user tries to get by url
        return HttpResponseRedirect(reverse('orders'))

    def form_valid(self, form):
        post_id = form.cleaned_data.get('cancel').id
        order = Order.objects.get(id=post_id)
        if datetime.now(timezone.utc) - order.order_date <= timedelta(minutes=3):
            # user has 3 minutes to discard order
            cancelled_order = CancelledOrder.objects.create(cancel=order)
            order.discarded = True
            order.save()
            cancelled_order.save()
        else:
            messages.info(self.request, 'You had only 3 minutes to do it')
        return HttpResponseRedirect(reverse('orders'))


class DiscardedOrdersViewList(PermissionRequiredMixin, ListView):
    """View for admin to see all discarded orders"""
    permission_required = 'request.user.is_superuser'
    model = CancelledOrder
    template_name = 'cancelled.html'
    paginate_by = 5
    login_url = 'products'


class DeleteDiscardedView(PermissionRequiredMixin, DeleteView):
    """View to submit the discard"""
    model = CancelledOrder
    permission_required = 'request.user.is_superuser'
    success_url = reverse_lazy('discarded_orders')


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    """Adding products by admin"""
    permission_required = 'request.user.is_superuser'
    model = Product
    http_method_names = ['get', 'post']
    fields = '__all__'
    template_name = 'change_product.html'
    success_url = "/products/"


class MainRedirectView(RedirectView):
    """Redirect from empty url"""
    url = "/products/"
