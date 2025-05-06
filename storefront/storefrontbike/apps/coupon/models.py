from django.db import models

# Create your models here.
class Coupon(models.Model):
    coupon_code = models.CharField(max_length = 50, unique = True)
    coupon_value = models.IntegerField() # Just to be flexible if you want to create a coupon with percentage 
    active = models.BooleanField(default = True)
    number_available = models.IntegerField(default = 1)
    number_used = models.IntegerField(default = 0)

    def __str__(self):
        return self.coupon_code
    
    def can_use(self): # Usability of coupons
        is_active = True

        if self.active == False:
            is_active = False

        if self.number_used >= self.number_available and self.number_available != 0:
            is_active = False

        return is_active
    
    def use(self): # Usage of function
        self.number_used += 1

        if self.number_used == self.number_available:
            self.active = False

        self.save()



