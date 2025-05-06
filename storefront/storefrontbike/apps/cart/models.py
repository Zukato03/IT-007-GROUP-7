from django.conf import settings
from django.db import models
from apps.store.models import Product

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username if self.user else 'Anonymous'}"

    def get_total_cost(self):
        items = self.items.all()
        print(f"Items in Cart: {list(items)}") 
        return sum(item.get_total_price() for item in items)

    def get_total_length(self):
        items = self.items.all()
        print(f"Items in Cart: {list(items)}")  
        return sum(item.quantity for item in items)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_total_price(self):
        return self.price * self.quantity

