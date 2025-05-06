from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from uuid import uuid4

# User Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_categories = models.TextField(blank=True)  # Stored as comma-separated string

    def __str__(self):
        return self.user.username

    def get_favorite_categories(self):
        return [cat.strip().lower() for cat in self.favorite_categories.split(',') if cat.strip()]

    def set_favorite_categories(self, categories):
        self.favorite_categories = ','.join(categories)

# Product
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField()
    short_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

 # Cart Item
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        lowest_price = self.product.prices.order_by('price').first()
        if lowest_price:
            return lowest_price.price * self.quantity
        return Decimal('0.00')

 # Generate order number
def generate_order_number():
    return f"ORD-{uuid4().hex[:8].upper()}"

# Order
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # New unique order number field
    order_number = models.CharField(
        max_length=20,
        unique=True,
        null=False,
        editable=False,
        default=generate_order_number,
    )

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # store at time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

 # Wishlist Item
class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

 # Wishlist Activity 
class WishlistActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=[('add', 'Add'), ('remove', 'Remove')])
    timestamp = models.DateTimeField(auto_now_add=True)

 # Vendor
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField()

    def __str__(self):
        return self.name

 # Product Price (Used for comparison)
class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    product_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.product.name} - £{self.price}"

 # Product View (Used for smart recommendations)
class ProductView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
