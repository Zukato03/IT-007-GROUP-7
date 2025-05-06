"""
URL configuration for storefrontbike project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views 
from django.contrib.auth import views as auth_views

from apps.cart.webhook import webhook #, paymongo_webhook
from apps.cart.views import cart_detail, success
from apps.core.views import frontpage, contact, about 
from apps.order.views import admin_order_pdf
from apps.store.views import product_detail, main_category_detail, sub_category_detail, search 
from apps.userprofile.views import signup, myaccount, update_user_info, signup_google#, forgot_username
#from apps.dashboard.views import admin_dashboard
#from apps.dashboard.admin import admin_site
from apps.newsletter.api import api_add_subscriber
from apps.coupon.api import api_can_use
from apps.store.api import api_add_to_cart, api_remove_from_cart, create_checkout_session, api_cart_items #,create_session_paymongo

from .sitemaps import StaticViewsSiteMap, MainCategorySitemap, SubCategorySitemap, ProductSitemap

sitemaps = {
    'static': StaticViewsSiteMap, 
    'main_category': MainCategorySitemap,
    'sub_category': SubCategorySitemap,
    'products': ProductSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_tools_stats/', include('admin_tools_stats.urls')),
    #path('admin/', admin_site.urls),
    #path('admin/', custom_admin_site.urls),
    #path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('search/', search, name='search'),
    path('', frontpage, name='frontpage'), 
    path('cart/', cart_detail, name='cart'),
    path('hooks/', webhook, name='webhook'),
    # path('paymongo_hooks/', paymongo_webhook, name='paymongo_webhook'),
    path('cart/success/', success, name='success'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('order/admin_order_pdf/<int:order_id>/', admin_order_pdf, name='admin_order_pdf'),



    # User Management
    
    path('myaccount/', myaccount, name='myaccount'),
    path('update_user_info/', update_user_info, name='update_user_info'),
    path('signup/', signup, name='signup'),
    path('signup_google/', signup_google, name='signup_google'),
    path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # For API used

    path('api/can_use/', api_can_use, name='api_can_use'),
    path('api/cart-items/', api_cart_items, name='api_cart_items'),
    path('api/create_checkout_session/', create_checkout_session, name='create_checkout_session'),
    # path('api/create_checkout_session_paymongo/', create_checkout_session_paymongo, name='create_checkout_session_paymongo'),
    path('api/add_to_cart', api_add_to_cart, name='api_add_to_cart'),
    path('api/remove_from_cart', api_remove_from_cart, name='api_remove_from_cart'),
    path('api/add_subscriber/', api_add_subscriber, name='api_add_subscriber'),

    # Store

    path('category/<slug:slug>/', main_category_detail, name='main_category_detail'),
    path('subcategory/<slug:slug>/', sub_category_detail, name='sub_category_detail'),
    path('<slug:category_slug>/<slug:slug>/', product_detail, name='product_detail'), # references the slug from the store/views.py
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
