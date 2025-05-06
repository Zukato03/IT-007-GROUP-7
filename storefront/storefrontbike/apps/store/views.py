import random
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from apps.cart.cart import Cart
from .models import Product, MainCategory, SubCategory, ProductReview

# Create your views here.
def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)
    sub_category = product.sub_category
    category = sub_category.main_category
    product.number_of_visits += 1
    product.last_visited = datetime.now()
    product.save()

    if request.method == 'POST' and request.user.is_authenticated:
        stars = request.POST.get('stars', 3)
        content = request.POST.get('content', '')
        review = ProductReview.objects.create(product=product, user=request.user, stars=stars, content=content)
        return redirect('product_detail', category_slug=category.slug, slug=slug)

    related_products = list(product.sub_category.products.filter(parent=None).exclude(id=product.id))

    if len(related_products) >= 3:
        related_products = random.sample(related_products, 3)

    if product.parent:
        return redirect('product_detail', category_slug=category.slug, slug=product.parent.slug)

    product_images = [{"product_thumbnail": product.product_thumbnail.url, "product_image": product.product_image.url}]
    for image in product.images_product.all():
        product_images.append({"product_thumbnail": image.product_thumbnail.url, "product_image": image.product_image.url})

    cart = Cart(request)
    product.in_cart = cart.has_product(product.id)

    
    # response_data = {
    #         'category': category.slug,
    #         'sub_category': sub_category.slug,
    #         'product': {
    #             'id': product.id,
    #             'title': product.title,
    #             'description': product.description,
    #             'price': product.price,
    #             'images': product_images,
    #             'in_cart': product.in_cart,
    #         },
    #         'related_products': [{'id': rel_prod.id, 'title': rel_prod.title} for rel_prod in related_products]  # Include IDs for related products
    #     }
    # return JsonResponse(response_data)

    


    context = {
        'category': category,
        'sub_category': sub_category,
        'product': product,
        'product_images': product_images,
        'related_products': related_products
    }

    return render(request, 'product_detail.html', context)


def main_category_detail(request, slug):
    category = get_object_or_404(MainCategory, slug=slug)
    subcategories = SubCategory.objects.filter(main_category=category)

    response_data = {
            'category_id': category.id,
            'category_title': category.title,
            'category_slug': category.slug,
            'category_ordering': category.main_ordering
        }

    # return JsonResponse(response_data)

    
    context = {
        'category': category,
        'menu_sub_categories': subcategories  # Pass only filtered subcategories
    }

    return render(request, 'main_category_detail.html', context)
    


def sub_category_detail(request, slug):
    sub_category = get_object_or_404(SubCategory, slug=slug)
    products = Product.objects.filter(sub_category=sub_category, parent=None)
    category = sub_category.main_category

    sub_category_images = [{"sub_category_image": sub_category.sub_category_image.url}] if sub_category.sub_category_image else []
    
    # response_data = {
    #         'category': category.slug,
    #         'sub_category': {
    #             'sub_category_title': sub_category.title,
    #             'sub_category_slug': sub_category.slug,
    #             'is_featured': sub_category.is_featured,
    #             'image': {
    #                 'sub_category_image': sub_category_images
    #             }
    #         } 
    #     }

    # return JsonResponse(response_data)
    
    
    
    context = {
        'sub_category': sub_category,
        'category': sub_category.main_category,
        'products': products
    }

    return render(request, 'sub_category_detail.html', context)

    



def search(request):
    query = request.GET.get('query')
    instock = request.GET.get('instock')
    price_from = request.GET.get('price_from', 0)
    price_to = request.GET.get('price_to', 100000)
    sorting = request.GET.get('sorting', '-date_added')
    
    products = Product.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)).filter(price__gte=price_from, price__lte=price_to)

    if instock:
        products = products.filter(number_available__gte=1)  # gte is greater than or equal


    # products_list = [{
    #         'id': product.id,
    #         'title': product.title,
    #         'description': product.description,
    #         'price': product.price,
    #         'number_available': product.number_available,
    #         'slug': product.slug,
    #         'image_url': product.product_image.url if product.product_image else None,  
    #     } for product in products]

    # response_data = {
    #         'products': products_list
    # }

    # return JsonResponse(response_data)

    
    context = {
        'query': query,
        'products': products.order_by(sorting),
        'instock': instock,
        'price_from': price_from,
        'price_to': price_to,
        'sorting': sorting
    }

    return render(request, 'search.html', context)

    








