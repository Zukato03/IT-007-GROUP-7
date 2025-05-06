from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

from .cart import Cart
from apps.order.models import Order

# Create your views here.
def cart_detail(request):
    print(f"Session Content: {dict(request.session)}")
    print(f"Request Headers: {request.headers}") 
    cart = Cart(request)

    print(f"[DEBUG] Cart items: {list(cart)}")
    productsstring = ''

    # Check if the cart is empty and prepare an appropriate response
    if not list(cart):  # If the cart is empty
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'cart': {
                    'products': [],
                    'total_cost': 0.0,
                },
                'customer_details': {}
            })

    print(f'Cart items: {list(cart)}')  # Debugging output

    for item in cart:
        product = item['product']
        url = '/%s/%s' % (product.sub_category.slug, product.slug)
        b = "{'id': '%s', 'title': '%s', 'price': '%s', 'quantity': '%s', 'total_price': '%s', 'product_thumbnail': '%s', 'url': '%s', 'number_available': '%s'}," % (
            product.id, product.title, product.price, item['quantity'], item['total_price'], product.product_thumbnail.url, url, product.number_available)

        productsstring += b

    first_name = last_name = email = contact_number = address = zip_code = ''
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email
        contact_number = request.user.userprofile.contact_number
        address = request.user.userprofile.address
        zip_code = request.user.userprofile.zip_code

    print(f'Products string: {productsstring}')

    context = {
        'cart': cart,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'contact_number': contact_number,
        'address': address,
        'zip_code': zip_code,
        'pub_key': settings.STRIPE_API_KEYS_PUBLISHABLE,
        'productsstring': productsstring,
    }

    return render(request, 'cart.html', context)

    
    # response_data = {
    #         'cart': {
    #             'products': [{
    #                 'id': product.id,
    #                 'title': product.title,
    #                 'description': product.description,
    #                 'price': product.price,
    #                 'number_available': product.number_available,
    #                 'slug': product.slug,
    #                 'image_url': product.product_image.url if product.product_image else None,
    #             } for item in cart],
    #             'total_cost': sum(item['total_price'] for item in cart)  
    #         },
    #         'customer_details': {
    #             'first_name': first_name,
    #             'last_name': last_name,
    #             'email': email,
    #             'contact_number': contact_number,
    #             'address': address,
    #             'zip_code': zip_code
    #         }
    #     }
    # return JsonResponse(response_data)
    
    '''
    response_data = {
            'cart': {
                'products': [{
                    'id': product.id,
                    'title': product.title,
                    'description': product.description,
                    'price': product.price,
                    'number_available': product.number_available,
                    'slug': product.slug,
                    'image_url': product.product_image.url if product.product_image else None,
                } for item in cart],
                'total_cost': sum(item['total_price'] for item in cart)  
            },
            'customer_details': {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'contact_number': contact_number,
                'address': address,
                'zip_code': zip_code
            }
        }
    return JsonResponse(response_data)

    '''
    
def success(request):
    cart = Cart(request)
    order_id = request.session.get('order_id')

    if order_id:
        try:
            order = Order.objects.get(pk=order_id)
            purchased_items = order.items.all()

            print(f"Purchased items: {[item.product.id for item in purchased_items]}")

            for item in purchased_items:
                print(f"Removing item with ID: {item.product.id} from cart.")
                cart.remove(item.product.id)

            # Clear the order_id from the session
            del request.session['order_id']
            print("Order ID cleared from session.")

        except Order.DoesNotExist:
            print("Order does not exist.")
        except Exception as e:
            print(f"Unexpected error in success view: {e}")

    return render(request, 'success.html')




