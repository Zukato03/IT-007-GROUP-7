from .models import MainCategory

def menu_main_categories(request):
    categories = MainCategory.objects.all()
    return {'menu_main_categories': categories}
