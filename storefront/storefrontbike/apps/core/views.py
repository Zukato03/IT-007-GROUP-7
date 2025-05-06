from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from apps.store.models import Product, SubCategory, MainCategory # Importing the Products inside the models.py in Store folder
from apps.cart.cart import Cart

def frontpage(request):
    cart = Cart(request)
    products = Product.objects.filter(is_featured=True)
    all_main_categories = MainCategory.objects.all()
    all_sub_categories = SubCategory.objects.all()
    all_products = Product.objects.all()
    featured_categories = SubCategory.objects.filter(is_featured=True)
    popular_products = Product.objects.all().order_by('-number_of_visits')[:4]
    recently_viewed_products = Product.objects.all().order_by('-last_visited')[:4]

    # data = {
    #         'featured_products': [
    #             {
    #                 'id': product.id,
    #                 'title': product.title,
    #                 'description': product.description,
    #                 'price': product.price,
    #                 'image': product.product_image.url if product.product_image else None  
    #             } for product in products
    #         ],
    #         'featured_categories': [
    #             {
    #                 'id': product.id,
    #                 'title': product.title,
    #                 'description': product.description,
    #                 'price': product.price,
    #                 'image': product.product_image.url if product.product_image else None  
    #             } for product in products
    #         ],
    #         'popular_products': [
    #             {
    #                 'id': product.id,
    #                 'title': product.title,
    #                 'description': product.description,
    #                 'price': product.price,
    #                 'image': product.product_image.url if product.product_image else None
    #             } for product in popular_products
    #         ],
    #         'recently_viewed': [
    #             {
    #                 'id': product.id,
    #                 'title': product.title,
    #                 'description': product.description,
    #                 'price': product.price,
    #                 'image': product.product_image.url if product.product_image else None
    #             } for product in recently_viewed_products
    #         ]
    #     }
    # return JsonResponse(data)

    
    # Render HTML template for non-JSON requests
    context = {
        'featured_categories': featured_categories,
        'products': products,
        'popular_products': popular_products,
        'recently_viewed_products': recently_viewed_products,
        'cart': cart
    }
    return render(request, 'frontpage.html', context)
    

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')
