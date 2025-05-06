from decimal import Decimal

from apps.store.models import Product
from .models import Cart as CartModel, CartItem

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None

        if self.user:
            user_carts = CartModel.objects.filter(user=self.user)
            if user_carts.exists():
                self.cart = user_carts.first()
                if user_carts.count() > 1:
                    for duplicate_cart in user_carts[1:]:
                        self.merge_carts(duplicate_cart, self.cart) 
            else:
                self.cart = CartModel.objects.create(user=self.user)
        else:
            cart_id = self.session.get('cart_id')
            if cart_id:
                try:
                    self.cart = CartModel.objects.get(id=cart_id)
                except CartModel.DoesNotExist:
                    # Create a new cart if the cart_id is not valid
                    self.cart = CartModel.objects.create(user=None)
                    self.session['cart_id'] = self.cart.id
            else:
                self.cart = CartModel.objects.create(user=None)
                self.session['cart_id'] = self.cart.id

    def get_or_create_cart(self):
        if self.user:
            cart, created = CartModel.objects.get_or_create(user=self.user)
        else:
            cart = None 
        return cart

    def has_product(self, product_id):
        if not hasattr(self, 'cart'):
            return False
        return CartItem.objects.filter(cart=self.cart, product_id=product_id).exists()

    def add(self, product, quantity=1, update_quantity=False):
        print(f"[DEBUG] Add called: Product ID={product.id}, Quantity={quantity}, Update Quantity={update_quantity}")
        if not hasattr(self, 'cart'):
            return

        cart_item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )

        if not created:  # If the cart item already exists
            if update_quantity:
                cart_item.quantity = quantity
            else:
                cart_item.quantity = quantity  # Set to the new quantity instead of incrementing
            cart_item.save()

        print(f"[DEBUG] CartItem status: ID={cart_item.id}, Quantity={cart_item.quantity}, Created={created}")
        self.cart.save()


    def remove(self, product_id):
        if not hasattr(self, 'cart'):
            return  

        try:
            product = Product.objects.get(id=product_id)
            cart_item = CartItem.objects.filter(cart=self.cart, product=product).first()
            
            if cart_item:
                cart_item.delete()
                print(f"Removed product: {product_id} from cart.")
            else:
                print(f"Product: {product_id} not found in the cart.")

        except Product.DoesNotExist:
            print(f"Product with ID: {product_id} does not exist.")


    def clear(self):
        if hasattr(self, 'cart'):
            self.cart.items.all().delete()

    def get_total_cost(self):
        total_cost = sum(Decimal(item.get_total_price()) for item in self.cart.items.all())
        print(f"Total cost calculated: {total_cost}")
        return total_cost

    def get_total_length(self):
        total_length = sum(item.quantity for item in self.cart.items.all())
        print(f"Total length calculated: {total_length}")  
        return total_length

    def __iter__(self):
        for item in self.cart.items.all():
            print(f'Yielding item: {item.product.id}, Quantity: {item.quantity}')
            yield {
                'product': item.product,
                'quantity': item.quantity,
                'total_price': item.get_total_price(),  
                'price': item.price,
            }

    def merge_carts(self, session_cart, user_cart):
        for item in session_cart.items.all():
            user_cart_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                defaults={'quantity': item.quantity, 'price': item.price}
            )
            if not created:
                user_cart_item.quantity += item.quantity
                user_cart_item.save()

        session_cart.delete() 










