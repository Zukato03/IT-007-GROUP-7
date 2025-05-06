from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from apps.store.models import MainCategory, SubCategory, Product

class StaticViewsSiteMap(Sitemap):
    def items(self):
        return ['frontpage', 'about', 'contact']
    
    def location(self, item):
        return reverse(item)

class MainCategorySitemap(Sitemap):
    def items(self):
        return MainCategory.objects.all()
    
class SubCategorySitemap(Sitemap):
    def items(self):
        return SubCategory.objects.all()
    
class ProductSitemap(Sitemap):
    def items(self):
        return Product.objects.all()
    
    def lastmode(self, obj):
        return obj.date_added
    
    