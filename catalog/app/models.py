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
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.title}: {self.amount}'


class Order(models.Model):
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, default=None)
    relationship = models.ManyToManyField(Product, through='SingleProductOrder')
    order_date = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.owner}: {self.order_date}'


class SingleProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    position = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.position}: {self.quantity}'


class CancelledOrder(models.Model):
    cancel = models.ForeignKey(Order, on_delete=models.CASCADE)
