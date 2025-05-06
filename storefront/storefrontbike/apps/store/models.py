from io import BytesIO
from django.core.files import File
from django.db import models
from PIL import Image
from django.contrib.auth.models import User
from django.db.models import F
from django.core.exceptions import ValidationError

# Create your models here.
# Database model
class MainCategory(models.Model):
    title = models.CharField(max_length = 255) # Character field for the database
    slug = models.SlugField(max_length = 255) # a description containing only letters, hyphens, numbers or underscores
    main_ordering = models.IntegerField(default=0)


    class Meta:
        verbose_name_plural = 'Main Categories' # Correcting the plural of the cataegory correct instead of categorys.
        ordering = ('main_ordering',)

    def __str__(self): # To see the title character in admin
        return self.title
    
    def get_absolute_url(self):
        return '/%s/' % (self.slug)


class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, related_name='sub_categories', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sub_ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    sub_category_image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    sub_category_thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Sub Categories'
        ordering = ('sub_ordering',)

    def __str__(self):
        return self.title
    
    def save_sub_category_image(self, *args, **kwargs):
        self.sub_category_thumbnail = self.make_sub_category_thumbnail(self.sub_category_image)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return '/%s/%s' % (self.main_category.slug, self.slug)
    
    def make_sub_category_thumbnail(self, image, size=(300, 200)):
        sub_category_img = Image.open(image)
        sub_category_img.convert('RGB')
        sub_category_img.thumbnail(size)

        sub_category_thumb_io = BytesIO()
        sub_category_img.save(sub_category_thumb_io, 'JPEG', quality=85)

        from os.path import basename
        sub_category_thumbnail = File(sub_category_thumb_io, name=basename(image.name))

        return sub_category_thumbnail
  
  
class Product(models.Model): # Adding the product in the database
    sub_category = models.ForeignKey(SubCategory, related_name='products', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='variants', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    is_featured = models.BooleanField(default=False)
    number_available = models.IntegerField(default=1)

    increase_by = models.IntegerField(default=0, blank=True, null=True)
    decrease_by = models.IntegerField(default=0, blank=True, null=True)

    product_image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    product_thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)

    date_added = models.DateTimeField(auto_now_add=True)

    number_of_visits = models.IntegerField(default=0)
    last_visited = models.DateTimeField(blank=True, null=True)


    class Meta:
        ordering = ('-date_added',) # Newest one comes first. You can remove the "-" if you want the oldest one to come first.

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.price <= 0:
            raise ValidationError({'price': "The price of the product cannot be less than or equal to 0."})
        
        if self.number_available < 0:
            raise ValidationError({'number_available': "The stock should not be less than 0."})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        
        if self.increase_by:
            self.number_available = F('number_available') + self.increase_by
        if self.decrease_by:
            self.number_available -= self.decrease_by
            if self.number_available - self.decrease_by < 0:
                self.number_available += self.decrease_by 
            else:
                self.number_available = F('number_available') - self.decrease_by
        
        super().save(*args, **kwargs)
        self.increase_by = 0
        self.decrease_by = 0
    
    """
    def save(self, *args, **kwargs):
        self.product_thumbnail = self.make_product_thumbnail(self.product_image)

        super().save(*args, **kwargs)
    """

    def get_product_thumbnail(self):
        if self.product_thumbnail: # Check if there's a thumbnail for products
            return self.product_thumbnail.url
        else: 
            if self.product_image: # Otherwise, it will check if there's an image of a product, then it will generate a thumbnail.
                self.product_thumbnail = self.make_product_thumbnail(self.product_image)
                self.save()
                return self.product_thumbnail.url
            else: # If there are still no images, it will return an empty string.
                return ''

    def get_absolute_url(self):
        return '/%s/%s' % (self.sub_category.slug, self.slug)
    
    def make_product_thumbnail(self, image, size=(300, 200)):
        product_img = Image.open(image)
        product_img.convert('RGB')
        product_img.thumbnail(size)

        product_thumb_io = BytesIO()
        product_img.save(product_thumb_io, 'JPEG', quality=85)

        from os.path import basename
        product_thumbnail = File(product_thumb_io, name=basename(image.name))

        return product_thumbnail
    
    def get_rating(self):
        total = sum(int(product_review['stars']) for product_review in self.product_reviews.values())

        if self.product_reviews.count() > 0:
            return total / self.product_reviews.count()
        else:
            return 0
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images_product', on_delete=models.CASCADE)

    product_image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    product_thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)

    def make_product_thumbnail(self, image, size=(300, 200)):
        product_img = Image.open(image)
        product_img.convert('RGB')
        product_img.thumbnail(size)

        product_thumb_io = BytesIO()
        product_img.save(product_thumb_io, 'JPEG', quality=85)

        from os.path import basename
        product_thumbnail = File(product_thumb_io, name=basename(image.name))

        return product_thumbnail

    def save(self, *args, **kwargs):
        self.product_thumbnail = self.make_product_thumbnail(self.product_image)

        super().save(*args, **kwargs)


class ProductReview(models.Model):
     product = models.ForeignKey(Product, related_name='product_reviews', on_delete=models.CASCADE)
     user = models.ForeignKey(User, related_name='product_reviews', on_delete=models.CASCADE)

     content = models.TextField(blank=True, null=True)
     stars = models.IntegerField()

     date_added = models.DateTimeField(auto_now_add=True)

     







