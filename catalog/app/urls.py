from django.http import HttpResponse
from django.urls import path

from .views import ProductCreateView, LogView, OutView, ProductViewList, RegistrateView, \
    ProductUpdateView, MainRedirectView, OrderViewList, DiscardedOrdersViewList, OrderDiscardView, \
    DeleteDiscardedView, OrderCreateView

urlpatterns = [
    path('', MainRedirectView.as_view(), name='empty'),
    path('product/', ProductCreateView.as_view(), name='create'),
    path('login/', LogView.as_view(), name='login'),
    path('thanks/', lambda x: HttpResponse("thanks"), name='thnx'),
    path('logout/', OutView.as_view(), name='logout'),
    path('main/', lambda x: HttpResponse('main')),
    path('orders/', OrderViewList.as_view(), name='orders'),
    path('orders/discard/', OrderDiscardView.as_view(), name='discard_order'),
    path('cancelled/', DiscardedOrdersViewList.as_view(), name='discarded_orders'),
    path('cancelled/delete/<int:pk>/', DeleteDiscardedView.as_view(), name='delete_discarded'),
    path('products/', ProductViewList.as_view(), name="products"),
    path('reg/', RegistrateView.as_view(), name='registrate'),
    path('products/buy/', OrderCreateView.as_view(), name='buy_product'),
    path('products/change/<int:pk>/', ProductUpdateView.as_view(), name='change_product'),
]