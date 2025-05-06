import datetime
import os
from decimal import Decimal

from random import randint

from apps.cart.cart import Cart

from apps.order.models import Order, OrderItem

def checkout(request, first_name, last_name, email, contact_number, address, zip_code, selected_product_ids, coupon_value=0):
    order = Order(
        first_name=first_name,
        last_name=last_name,
        email=email,
        contact_number=contact_number,
        address=address,
        zip_code=zip_code,
    )

    if request.user.is_authenticated:
        order.user = request.user

    order.save()  # Saving the order to the database

    cart = Cart(request)

    for item in cart:
        product = item['product']
        if str(product.id) in selected_product_ids:  
            price = Decimal(item['price']) 

            if coupon_value > 0:
                price *= (1 - Decimal(coupon_value) / Decimal(100))  
            
            OrderItem.objects.create(order=order, product=product, price=price, quantity=item['quantity'])

    return order.id



