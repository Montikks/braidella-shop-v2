from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Product

class Command(BaseCommand):
    help = "Vloží demo kategorie a produkty (CZ, ceny s DPH)."

    def handle(self, *args, **options):
        data = {
            "Kanekalon copánky": [
                ("Braidella Basic 60cm", 349, 50, "Základní syntetické vlasy pro copánky, délka 60 cm."),
                ("Braidella Premium 80cm", 499, 30, "Prémiové vlasy pro copánky, délka 80 cm."),
            ],
            "Doplňky": [
                ("Gumičky bez spoje (100 ks)", 79, 200, "Jemné gumičky vhodné pro ukončení copánků."),
                ("Jehla pro navlékání", 59, 100, "Pomůcka pro rychlé protahování pramenů."),
            ],
        }

        cats = prods = 0
        for cat_name, products in data.items():
            cat_slug = slugify(cat_name)  # ← ASCII slug (např. 'doplňky' -> 'doplnky')
            cat, created = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={"name": cat_name},
            )
            cats += int(created)
            for name, price, stock, short in products:
                prod_slug = slugify(name)
                _, created_p = Product.objects.get_or_create(
                    slug=prod_slug,
                    defaults={
                        "category": cat,
                        "name": name,
                        "price": price,
                        "stock": stock,
                        "short_description": short,
                        "description": short,
                        "active": True,
                    },
                )
                prods += int(created_p)
        self.stdout.write(self.style.SUCCESS(f"Hotovo. Nové kategorie: {cats}, nové produkty: {prods}"))
