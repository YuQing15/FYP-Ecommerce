from django.contrib import admin
from .models import (
    Profile, Product, CartItem, Order,
    WishlistItem, WishlistActivity, Vendor,
    ProductPrice, ProductView
)

admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(WishlistItem)
admin.site.register(WishlistActivity)
admin.site.register(Vendor)
admin.site.register(ProductPrice)
admin.site.register(ProductView)