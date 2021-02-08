from datetime import datetime, timezone, timedelta
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, ListView, FormView, UpdateView, RedirectView
from .forms import ProductForm, RegForm
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

    def get(self, request, *args, **kwargs): # Redirect to main page if authenticated
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/products')
        else:
            return super().get(request=request, *args, **kwargs)


class OutView(LogoutView):
    login_url = '/products'
    template_name = 'index.html'
    next_page = '/products'


class ProductCreateView(PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    permission_required = 'request.user.is_superuser'
    model = Product
    form_class = ProductForm
    success_url = '/product'
    template_name = 'index.html'


class ProductViewList(ListView):
    model = Product
    template_name = 'products.html'
    paginate_by = 3
    ordering = ['-amount', 'price']
    extra_context = {'name': 'products'}


class OrderCreateView(CreateView):
    model = Order
    fields = '__all__'

    def get(self, request, *args, **kwargs):
        if request.POST.get('id') is None:
            return HttpResponseRedirect('/products/')

    def get_success_url(self):
        return f"/products/?page={self.request.POST.get('page')}"

    def post(self, request, *args, **kwargs): # Creating an order
        user_amount = request.POST.get('amount')
        if user_amount <= 0:
            messages.error(request, 'Sorry, wrong number of product to buy')
            return HttpResponseRedirect(self.get_success_url())
        user_amount = int(user_amount)
        product_id = request.POST['id']
        product = Product.objects.get(id=product_id)
        if user_amount <= product.amount:
            user_id = request.user.id
            user = MyUser.objects.get(id=user_id)
            if user.balance - (product.price * user_amount) >= 0:
                user.balance -= product.price * user_amount
                product.amount -= user_amount
                ord = Order.objects.create(owner=user, position=product, quantity=user_amount)
                ord.save()
                product.save()
                user.save()
                messages.info(request, 'Thnx 4 order')
            else:
                messages.error(request, 'Sorry, u dont have enough money')
        else:
            messages.error(request, 'Sorry, wrong number of product to buy')
        return HttpResponseRedirect(self.get_success_url())


class OrderViewList(LoginRequiredMixin, ListView):
    login_url = "/login"
    model = Order
    template_name = 'orders.html'
    paginate_by = 5
    ordering = ['-order_date']

    def get_queryset(self):
        queryset = Order.objects.filter(owner__id=self.request.user.id)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
        queryset = queryset.order_by(*ordering)
        return queryset


class OrderDiscardView(LoginRequiredMixin, CreateView):
    login_url = '/login/'

    def post(self, request, *args, **kwargs): # Discarding the order
        post_id = request.POST.get('id')
        if post_id is None:
            return HttpResponseRedirect('/orders')
        order = Order.objects.get(id=post_id)
        page = request.POST.get('page')
        if datetime.now(timezone.utc) - order.order_date <= timedelta(minutes=3):
            cancelled_order = CancelledOrder.objects.create(cancel=order)
            order.discarded = True
            order.save()
            cancelled_order.save()
        else:
            messages.info(request, 'You had only 3 minutes to do it')
        return HttpResponseRedirect(f"/orders/?page={page}")


class DiscardedOrdersViewList(PermissionRequiredMixin, ListView):
    permission_required = 'request.user.is_superuser'
    model = CancelledOrder
    fields = '__all__'
    template_name = 'cancelled.html'
    paginate_by = 5
    login_url = 'products'


class DeleteDiscardedView(PermissionRequiredMixin, CreateView):
    permission_required = 'request.user.is_superuser'

    def post(self, request, *args, **kwargs): # Submitting the cancel of order
        post_id = request.POST.get('id')
        if post_id is None:
            return HttpResponseRedirect('products/')
        usr_id = CancelledOrder.objects.get(id=post_id).cancel.owner.id
        usr = MyUser.objects.get(id=usr_id)
        price = CancelledOrder.objects.get(id=post_id).cancel.position.price
        amount = CancelledOrder.objects.get(id=post_id).cancel.quantity
        usr.balance += amount * price
        usr.save()
        product = CancelledOrder.objects.get(id=post_id).cancel.position
        product.amount += amount
        product.save()
        CancelledOrder.objects.get(id=post_id).cancel.delete()
        return HttpResponseRedirect('/cancelled')


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'request.user.is_superuser'
    model = Product
    fields = '__all__'
    template_name = 'change_product.html'
    success_url = "/products"


class MainRedirectView(RedirectView):
    url = "/products/"
