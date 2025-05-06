import requests
from .models import Product, Vendor, ProductPrice

def fetch_prices(product_name):
    
    # Fetching price data from external vendor APIs and updates the database.    
    API_ENDPOINTS = {
        
    }

    price_data = []

    for vendor_name, url in API_ENDPOINTS.items():
        try:
            response = requests.get(url, params={"query": product_name}, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching data from {vendor_name}: {e}")
            continue

        try:
            data = response.json()
            for item in data.get("results", []):
                vendor, _ = Vendor.objects.get_or_create(name=vendor_name, website=url)

                try:
                    product = Product.objects.get(name=product_name)
                except Product.DoesNotExist:
                    print(f"⚠️ Product not found: {product_name}")
                    continue

                price_entry, created = ProductPrice.objects.get_or_create(
                    product=product,
                    vendor=vendor,
                    defaults={"price": item["price"]}
                )

                if not created:
                    price_entry.price = item["price"]
                    price_entry.save()

                price_data.append({
                    "vendor": vendor.name,
                    "price": item["price"],
                    "product_url": item.get("url", "#")
                })

        except ValueError:
            print(f"❌ Failed to parse JSON from {vendor_name}")
            continue

    return price_data
