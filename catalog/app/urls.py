from django.http import HttpResponse
from django.urls import path

from .views import ProductCreateView, LogView, OutView, ProductViewList, RegistrateView, \
    ProductUpdateView, MainRedirectView, OrderViewList, DiscardedOrdersViewList, OrderDiscardView, \
    DeleteDiscardedView, OrderCreateView

urlpatterns = [
    path('', MainRedirectView.as_view()),
    path('product/', ProductCreateView.as_view()),
    path('login/', LogView.as_view()),
    path('thanks/', lambda x: HttpResponse("thanks"), name='thnx'),
    path('logout/', OutView.as_view()),
    path('main/', lambda x: HttpResponse('main')),
    path('orders/', OrderViewList.as_view(), name='orders'),
    path('orders/discard/', OrderDiscardView.as_view()),
    path('cancelled/', DiscardedOrdersViewList.as_view()),
    path('cancelled/delete/', DeleteDiscardedView.as_view()),
    path('products/', ProductViewList.as_view(), name="products"),
    path('reg/', RegistrateView.as_view()),
    path('products/buy/', OrderCreateView.as_view()),
    path('products/change/<int:pk>/', ProductUpdateView.as_view()),
]