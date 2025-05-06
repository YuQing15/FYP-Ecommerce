from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Profile, Product, CartItem, WishlistItem, Order, ProductPrice, ProductView, OrderItem
from .services import fetch_prices
import random
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def recommendation(request):
    products = Product.objects.all()
    return render(request, 'recommendation.html', {'products': products})

def get_recommendations(request):
    categories = request.GET.get('categories', '').split(',')
    recommended_products = []

    for category in categories:
        products = list(Product.objects.filter(category=category))
        recommended_products.extend(random.sample(products, min(2, len(products))))

    data = [
        {
            "name": p.name,
            "image_url": p.image_url,
            "price": p.prices.order_by('price').first().price if p.prices.exists() else None,
            "short_description": p.short_description
        }
        for p in recommended_products
    ]
    return JsonResponse(data, safe=False)

def home(request):
    return render(request, 'home.html')

def products(request):
    query = request.GET.get('q', '').strip()

    if query:
        products = Product.objects.filter(name__icontains=query).distinct()
    elif request.user.is_authenticated:
        try:
            profile = request.user.profile
            raw_categories = profile.get_favorite_categories()
            preferred_categories = [cat.strip().lower() for cat in raw_categories if cat.strip()]

            if preferred_categories:
                preferred_products = []
                for cat in preferred_categories:
                    category_products = list(Product.objects.filter(category=cat).distinct())
                    preferred_products.extend(category_products)

                preferred_ids = [p.id for p in preferred_products]
                other_products = Product.objects.exclude(id__in=preferred_ids).distinct()
                products = preferred_products + list(other_products)
            else:
                products = Product.objects.all().distinct()
        except Profile.DoesNotExist:
            products = Product.objects.all().distinct()
    else:
        products = Product.objects.all().distinct()

    for product in products:
        store_price = product.prices.filter(vendor__name__icontains="our store").first()
        product.store_price = store_price

    return render(request, 'products.html', {'products': products, 'query': query})

def about(request): 
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        messages.success(request, 'Thanks for contacting us! We’ll get back to you shortly.')
        return redirect('contact')
    return render(request, 'contact.html')

def account(request): 
    return render(request, 'account.html')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, "checkout.html", {"cart_items": cart_items, "total": total})

@login_required
def create_checkout_session(request):
    return redirect('payment_success')

@login_required
def payment_success(request):
    return render(request, "payment_success.html")

@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('checkout')

    total_price = sum(item.subtotal() for item in cart_items)

    # Create the order
    order = Order.objects.create(
        user=request.user,
        full_name=request.user.username,
        email=request.user.email,
        address="N/A",  # Or collect this in a form
        total_price=total_price,
        created_at=timezone.now()
    )

    # Save each item into OrderItem
    for item in cart_items:
        lowest_price = item.product.prices.order_by('price').first()
        if lowest_price:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=lowest_price.price
            )

    # Clear the cart
    cart_items.delete()
    messages.success(request, "Your order has been placed successfully!")
    return redirect('payment_success')

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "orders.html", {"orders": orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if created:
        return JsonResponse({"message": f"{product.name} added to wishlist!", "status": "success"})
    return JsonResponse({"message": f"{product.name} is already in your wishlist!", "status": "info"})

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    wishlist_item.delete()
    return JsonResponse({"message": "Item removed from wishlist!", "status": "success"})

@login_required
def add_to_basket(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    cart_item.save()
    messages.success(request, f"{product.name} added to basket!")
    return redirect('checkout')

@login_required
def delete_from_basket(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.warning(request, f"Removed {cart_item.product.name} from basket!")
    return redirect('checkout')

@login_required
def remove_from_basket(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.info(request, f"Updated basket!")
    return redirect('checkout')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    prices = ProductPrice.objects.filter(product=product)
    updated_prices = []
    for price in prices:
        real_time_price = fetch_real_time_price(price)
        price.real_time_price = real_time_price  
        updated_prices.append(price)
    return render(request, 'product_detail.html', {'product': product, 'prices': updated_prices})

def get_price_comparison(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    price_comparison = fetch_prices(product.name)
    return JsonResponse({"prices": price_comparison})

def fetch_real_time_price(product_price):
    try:
        if not product_price.product_url:
            return product_price.price

        response = requests.get(product_price.product_url, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Add vendor-specific scraping rules here
        return product_price.price  # Default fallback
    except Exception as e:
        print(f"Error fetching price: {e}")
        return product_price.price

def compare_prices(request, product_id):
    product = Product.objects.get(id=product_id)
    prices = product.prices.all()
    real_time_prices = []
    for price in prices:
        real_time_price = fetch_real_time_price(price)
        real_time_prices.append({
            'vendor': price.vendor,
            'price': real_time_price,
            'last_updated': price.last_updated,
            'link': price.vendor.website
        })
    return render(request, 'compare_prices.html', {'product': product, 'prices': real_time_prices})

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        login(request, user)  # Automatically log in after sign up
        messages.success(request, "Account created and logged in!")
        return redirect("dashboard")  # Redirect to dashboard
    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')
        messages.error(request, "Invalid credentials.")
    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")

@login_required
def profile(request):
    return render(request, "profile.html", {"user": request.user})

@login_required
def dashboard(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found")
        return redirect('login')

    cart_items = CartItem.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    categories = ['glasses', 'bracelets', 'necklaces', 'rings', 'earrings', 'bags']

    return render(request, 'dashboard.html', {
        'profile': user_profile,
        'cart_items': cart_items,
        'orders': orders,
        'wishlist_items': wishlist_items,
        'categories': categories 
    })

@require_POST
@login_required
def update_preferences(request):
    categories = request.POST.getlist('favorite_categories')
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.favorite_categories = ','.join(categories)
    profile.save()
    messages.success(request, "Preferences updated successfully!")
    return redirect('dashboard')

@require_POST
@login_required
def reset_preferences(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.favorite_categories = ''
    profile.save()
    messages.success(request, "Preferences reset successfully!")
    return redirect('dashboard')

def ar_tryon(request):
    return render(request, 'ar_tryon.html')

def track_product_view(request, product_id):
    if request.user.is_authenticated:
        ProductView.objects.create(user=request.user, product_id=product_id)
    return JsonResponse({'status': 'tracked'})

@login_required
def smart_recommendations(request):
    viewed_products = ProductView.objects.filter(user=request.user).values_list("product_id", flat=True)
    recommended = Product.objects.filter(
        category__in=Product.objects.filter(id__in=viewed_products).values_list("category", flat=True)
    ).exclude(id__in=viewed_products).distinct()[:10]

    for product in recommended:
        store_price = product.prices.filter(vendor__name__icontains="our store").first()
        product.store_price = store_price

    return render(request, 'smart_recommendations.html', {'products': recommended})
