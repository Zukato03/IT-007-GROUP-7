from django.contrib import admin
from django import forms
from django.db.models import F
from .models import MainCategory, SubCategory, Product, ProductImage, ProductReview 
from django.db.models import Sum
from django.core.exceptions import ValidationError


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        increase_by = cleaned_data.get('increase_by', 0)
        decrease_by = cleaned_data.get('decrease_by', 0)
        number_available = cleaned_data.get('number_available', 0)

        # Validate stock changes
        if decrease_by > 0 and (number_available - decrease_by) < 0:
            raise forms.ValidationError({
                'decrease_by': "The stock cannot go below 0. Please adjust the 'Decrease by' field."
            })

        return cleaned_data
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm 
    list_display = ('title', 'sub_category', 'number_available', 'price')

    def save_model(self, request, obj, form, change):
        # Adjust stock levels safely
        if obj.increase_by:
            obj.number_available += obj.increase_by

        if obj.decrease_by:
            obj.number_available -= obj.decrease_by

        # Reset increase_by and decrease_by
        obj.increase_by = 0
        obj.decrease_by = 0

        # Save the product
        super().save_model(request, obj, form, change)

    def total_purchases(self, obj):
        total = obj.items.aggregate(total=Sum('quantity'))['total']
        return total if total else 0  
    
    readonly_fields = ('total_purchases',)
    total_purchases.short_description = 'Total Purchases'

# Register your models here.
admin.site.register(MainCategory) # Register the new database in store
admin.site.register(SubCategory) 
#admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductReview)
