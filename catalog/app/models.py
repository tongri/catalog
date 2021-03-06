from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class MyUser(AbstractUser):
    avatar = models.ImageField(blank=True, null=True)
    balance = models.PositiveIntegerField(default=10000, blank=False)


class Product(models.Model):
    title = models.CharField(max_length=30)
    desc = models.CharField(max_length=150)
    photo = models.ImageField(blank=True)
    amount = models.PositiveSmallIntegerField(default=1)
    price = models.PositiveSmallIntegerField(default=1000)

    def __str__(self):
        return f'{self.title}: {self.amount}'


class Order(models.Model):
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, default=None, related_name='orders')
    position = models.ForeignKey(Product, on_delete=models.CASCADE, default=None)
    quantity = models.PositiveSmallIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    discarded = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.owner}: {self.order_date}'


class CancelledOrder(models.Model):
    cancel = models.ForeignKey(Order, on_delete=models.CASCADE)
    cancel_date = models.DateTimeField(auto_now_add=True)
