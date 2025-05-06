# For testing real-time price updates via scraping.
# currently not in use

from django.core.management.base import BaseCommand
from myapp.models import ProductPrice
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils.timezone import make_aware

class Command(BaseCommand):
    help = "Update product prices from vendor websites"

    def handle(self, *args, **kwargs):
        for price_entry in ProductPrice.objects.all():
            try:
                url = price_entry.link
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                # Example: parse price from a class or ID (adjust per vendor!)
                price_element = soup.select_one(".price, .product-price, .pdp-price")  # customise as needed
                if price_element:
                    raw_price = price_element.text.strip().replace("£", "").replace(",", "")
                    new_price = float(raw_price)

                    price_entry.price = new_price
                    price_entry.last_updated = make_aware(datetime.now())
                    price_entry.save()
                    self.stdout.write(f"Updated price for {price_entry.vendor.name}: £{new_price}")
                else:
                    self.stdout.write(f"Price not found on {url}")
            except Exception as e:
                self.stderr.write(f"Error updating {price_entry.vendor.name}: {e}")