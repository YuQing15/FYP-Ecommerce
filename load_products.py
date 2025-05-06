from myapp.models import Product, Vendor, ProductPrice

# Utility to create or update product with prices
def create_product_with_prices(name, category, image_url, url, short_description, vendor_prices):
    product, _ = Product.objects.get_or_create(
        name=name,
        category=category,
        image_url=image_url,
        url=url,
        short_description=short_description
    )

    for vendor_data in vendor_prices:
        vendor, _ = Vendor.objects.get_or_create(name=vendor_data['name'], website=vendor_data['website'])
        ProductPrice.objects.get_or_create(product=product, vendor=vendor, price=vendor_data['price'], product_url=vendor_data['url'])

# Product: Miu Miu Glasses
create_product_with_prices(
    name="Miu Miu Glasses",
    category="glasses",
    image_url="https://i.ibb.co/6mPDG4N/miumiu-transparent.png",
    url="http://127.0.0.1:8000/products/",
    short_description="Stylish Miu Miu transparent glasses.",
    vendor_prices=[
        {"name": "Cettire", "website": "https://www.cettire.com", "price": 222.00, "url": "https://www.cettire.com/en-gb/products/miu-miu-eyewear-mu52xs-sunglasses-1552t3?variant=47652892010673"},
        {"name": "Mytheresa", "website": "https://www.mytheresa.com", "price": 254.00, "url": "https://www.mytheresa.com/en-gb/miu-miu-oval-acetate-sunglasses-1393087.html"}
    ]
)

# Product: Ray-Ban Glasses
create_product_with_prices(
    name="Ray-Ban Glasses",
    category="glasses",
    image_url="https://i.ibb.co/YcD5zr9/rayban-glasses-transparent.png",
    url="http://127.0.0.1:8000/products/",
    short_description="Classic Ray-Ban eyewear with modern design.",
    vendor_prices=[
        {"name": "Pretavoir", "website": "https://www.pretavoir.co.uk", "price": 104.17, "url": "https://www.pretavoir.co.uk/products/ray-ban-rx3447v-2500-round-metal-glasses"},
        {"name": "Amazon", "website": "https://www.amazon.co.uk", "price": 104.99, "url": "https://www.amazon.co.uk/Ray-Ban-Round-Metal-Eyeglasses/dp/B00D0JAW6A"}
    ]
)

# Product: Chanel Glasses
create_product_with_prices(
    name="Chanel Glasses",
    category="glasses",
    image_url="https://i.ibb.co/jhwncM6/chanel-transparent.png",
    url="http://127.0.0.1:8000/products/",
    short_description="Elegant Chanel transparent glasses.",
    vendor_prices=[
        {"name": "Fashion Eyewear", "website": "https://www.fashioneyewear.co.uk", "price": 280.00, "url": "https://www.fashioneyewear.co.uk/products/chanel-ch3416b-eyeglasses-1536"},
        {"name": "Pretavoir", "website": "https://www.pretavoir.co.uk", "price": 275.00, "url": "https://www.pretavoir.co.uk/products/chanel-ch3416b-glasses"}
    ]
)

# Product: Ray-Ban 2 Glasses
create_product_with_prices(
    name="Ray-Ban 2 Glasses",
    category="glasses",
    image_url="https://i.ibb.co/1Q3mKj3/rayban2-glasses-transparent.png",
    url="http://127.0.0.1:8000/products/",
    short_description="Another model of Ray-Ban's iconic eyewear.",
    vendor_prices=[
        {"name": "Opticians Direct", "website": "https://www.opticiansdirect.co.uk", "price": 94.99, "url": "https://www.opticiansdirect.co.uk/ray-ban-rx3447v-2500"},
        {"name": "Pretavoir", "website": "https://www.pretavoir.co.uk", "price": 105.00, "url": "https://www.pretavoir.co.uk/products/ray-ban-rx3447v-2500-round-metal-glasses"}
    ]
)
