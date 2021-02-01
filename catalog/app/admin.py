from django.contrib import admin
from .models import MyUser, Order, Product, SingleProductOrder, CancelledOrder
# Register your models here.

admin.site.register(MyUser)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(SingleProductOrder)
admin.site.register(CancelledOrder)
