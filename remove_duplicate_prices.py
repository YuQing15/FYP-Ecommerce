from collections import defaultdict
from myapp.models import ProductPrice

def remove_duplicate_prices(dry_run=True):
    grouped = defaultdict(list)
    for price in ProductPrice.objects.all():
        key = (price.product.id, price.vendor.id, float(price.price))
        grouped[key].append(price)

    deleted_count = 0
    for key, duplicates in grouped.items():
        if len(duplicates) > 1:
            to_delete = duplicates[1:]
            if dry_run:
                print(f"[DRY RUN] Would delete {len(to_delete)} duplicates for {key}")
            else:
                for p in to_delete:
                    p.delete()
                    deleted_count += 1

    if dry_run:
        print("✅ Dry run complete. No changes made.")
    else:
        print(f"✅ Done! Removed {deleted_count} duplicate ProductPrice entries.")
