from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Userprofile

class UserprofileInline(admin.StackedInline):
    model = Userprofile
    can_delete = False 
    verbose_name_plural = 'Additional Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserprofileInline, )

    list_display = ('username', 'email', 'first_name', 'last_name', 'get_contact_number', 'get_address', 'get_zip_code')
    list_select_related = ('userprofile', )

    def get_contact_number(self, instance):
        return instance.userprofile.contact_number
    get_contact_number.short_description = 'Contact Number'

    def get_address(self, instance):
        return instance.userprofile.address
    get_address.short_description = 'Address'

    def get_zip_code(self, instance):
        return instance.userprofile.zip_code
    get_zip_code.short_description = 'Zip Code'

    search_fields = ('username', 'email', 'userprofile__contact_number', 'userprofile__address', 'userprofile__zip_code')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
