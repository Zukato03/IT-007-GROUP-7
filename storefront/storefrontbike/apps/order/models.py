from django.db import models
from django.contrib.auth.models import User

from apps.store.models import Product

# Create your models here.
class Order(models.Model):
    ORDERED = 'ordered'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'

    STATUS_CHOICES = (
        (ORDERED, 'Ordered'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered')
    )

    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, blank=True, null=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    zip_code = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=100, default='00000000000')

    order_created_at = models.DateTimeField(auto_now_add=True)

    paid = models.BooleanField(default=False)
    paid_amount = models.FloatField(blank=True, null=True)
    used_coupon = models.CharField(max_length = 50, blank = True, null = True)

    payment_intent = models.CharField(max_length=300, blank=True, null=True)  

    ordered_date = models.DateTimeField(blank=True, null=True)

    shipped_date = models.DateTimeField(blank=True, null=True)
    shipped_status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = ORDERED)

    delivered_date = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return '%s' % self.first_name
    
    def get_total_quantity(self):
        return sum(int(item.quantity) for item in self.items.all())

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.DO_NOTHING)
    price = models.FloatField()
    quantity = models.IntegerField(default=1)

    def __str__ (self):
        return '%s' % self.id
    
class PaymentTracking(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    order_id = models.PositiveIntegerField()
