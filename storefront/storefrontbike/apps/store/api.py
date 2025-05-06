import json
import stripe
import requests

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.cart.cart import Cart
from apps.order.utils import checkout
from .models import Product
from apps.order.models import Order, PaymentTracking, OrderItem
from apps.coupon.models import Coupon

def api_cart_items(request):
    if request.method == 'GET':
        cart = Cart(request)
        cart_items = []

        for item in cart:
            product = item['product']
            cart_items.append({
                'id': product.id,
                'title': product.title,
                'price': product.price,
                'quantity': item['quantity'],
                'total_price': item['total_price'],
                'product_thumbnail': product.product_thumbnail.url,
                'number_available': product.number_available,
                'url': f"/{product.sub_category.slug}/{product.slug}",
            })

        return JsonResponse({'cart_items': cart_items})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def api_add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        cart = Cart(request)

        try:
            product = Product.objects.get(id=product_id)
            cart.add(product, quantity)
            print("Added to cart")
            return JsonResponse({'success': True})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def api_remove_from_cart(request):
    data = json.loads(request.body)
    jsonresponse = {'success': True}
    product_id = str(data['product_id'])

    cart = Cart(request)
    cart.remove(product_id)
    print("Removed from cart")

    return JsonResponse(jsonresponse)


def create_checkout_session(request):
    data = json.loads(request.body)

    # Coupon handling
    coupon_code_get = data.get('coupon_code', '') 
    coupon_value = 0

    if coupon_code_get:
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code_get)
            if coupon.can_use():
                coupon_value = coupon.coupon_value
                coupon.use()
        except Coupon.DoesNotExist:
            pass 

    cart = Cart(request)
    stripe.api_key = settings.STRIPE_API_KEYS_HIDDEN
    items = []

    selected_product_ids = [str(pid) for pid in data.get('selected_products', [])]

    total_price = 0.00
    for item in cart:
        product = item['product']

        if str(product.id) in selected_product_ids:
            price = int(product.price * 100) 

            if coupon_value > 0:
                if coupon_value < 100:  
                    price = int(price * (1 - coupon_value / 100)) 
                else:
                    price = 0 

            if price < 0:
                price = 0
            
            obj = {
                'price_data': {
                    'currency': 'php',
                    'product_data': {
                        'name': product.title
                    },
                    'unit_amount': price
                },
                'quantity': item['quantity']
            }
            items.append(obj)

            total_price += (price / 100) * item['quantity'] 

    if not items:
        return JsonResponse({'error': 'No items to checkout'}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        success_url='http://127.0.0.1:8000/cart/success/',
        cancel_url='http://127.0.0.1:8000/cart/',
    )

    # Create order
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    contact_number = data['contact_number']
    address = data['address']
    zip_code = data['zip_code']

    order_id = checkout(request, first_name, last_name, email, contact_number, address, zip_code, selected_product_ids, coupon_value)

    try:
        order = Order.objects.get(pk=order_id)
        order.paid_amount = total_price
        order.payment_intent = session.id  
        order.used_coupon = coupon_code_get if coupon_value > 0 else None
        order.save()

        PaymentTracking.objects.create(session_id=session.id, order_id=order.id)

        return JsonResponse({'session': session})

    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return JsonResponse({'error': 'Unable to create order'}, status=500)


# """
# def create_checkout_session_paymongo(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON format'}, status=400)

#     url = "https://api.paymongo.com/v1/checkout_sessions"

#     # Coupon handling
#     coupon_code_get = data.get('coupon_code', '') 
#     coupon_value = 0

#     if coupon_code_get:
#         try:
#             coupon = Coupon.objects.get(coupon_code=coupon_code_get)
#             if coupon.can_use():
#                 coupon_value = coupon.coupon_value
#                 coupon.use()
#         except Coupon.DoesNotExist:
#             return JsonResponse({'error': 'Invalid coupon code'}, status=400)

#     cart = Cart(request)
    
#     headers = {
#         'Content-Type': 'application/json',
#         "authorization": "Basic c2tfdGVzdF9jNE5yNkJ4eDJESHZRZjlMaFR6QW8zQVM6",
#         "accept": "application/json",
#     }

#     items = []
#     selected_product_ids = data.get('selected_products', [])
    
#     for item in cart:
#         product = item['product']
#         if product.id not in selected_product_ids:  
#             continue
            
#         price = int(product.price * 100)

#         if coupon_value > 0:
#             price = int(price * (1 - coupon_value / 100))

#         obj = {
#             'amount': price,
#             'currency': 'PHP', 
#             'description': product.title,
#             'quantity': item['quantity'],
#             'name': product.title,
#         }
#         items.append(obj)

#     print("Received data:", data)

#     if not items:
#         return JsonResponse({'error': 'No selected products for checkout'}, status=400)

#     payload = {
#         "data": {
#             "attributes": {
#                 "amount": sum(item['amount'] for item in items),
#                 "currency": "PHP",
#                 "description": "Order Checkout",
#                 "line_items": items,
#                 "payment_method_types": ['card', 'paymaya', 'gcash'],
#                 "success_url": "http://127.0.0.1:8000/cart/success/",
#                 "cancel_url": "http://127.0.0.1:8000/cart/",
#                 "capture_type": "automatic",
#             }
#         }
#     }

#     print("Payload to Paymongo:", json.dumps(payload, indent=4))

#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response_data = response.json()

#         print("Request Payload:", json.dumps(payload, indent=4))
#         print("Response Status Code:", response.status_code)
#         print("Response Data:", response_data)

#         if response.status_code == 200:
#             session_id = response_data['data']['id']
#             return JsonResponse({'session_id': session_id})
#         else:
#             print(f"Paymongo API Error: {response_data}")
#             return JsonResponse({'error': f"Paymongo session error: {response_data['errors']}"}, status=500)

#     except Exception as e:
#         print(f"Error creating Paymongo session: {str(e)}")
#         return JsonResponse({'error': 'Unable to create Paymongo session'}, status=500)

# """
