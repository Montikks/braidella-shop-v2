from django.core.management.base import BaseCommand
from apps.shipping.models import ShippingMethod

class Command(BaseCommand):
    help = "Naplní databázi výchozími způsoby dopravy"

    def handle(self, *args, **options):
        shipping_data = [
            # Zásilkovna – jen výdejní místo
            {
                "code": "zasilkovna-pickup",
                "name": "Zásilkovna – výdejní místo",
                "price": 79,
                "active": True,
            },
            # PPL
            {
                "code": "ppl-address",
                "name": "PPL – doručení na adresu",
                "price": 129,
                "active": True,
            },
            {
                "code": "ppl-pickup",
                "name": "PPL – výdejní místo",
                "price": 99,
                "active": True,
            },
            # Balíkovna
            {
                "code": "balikovna-address",
                "name": "Balíkovna – doručení na adresu",
                "price": 119,
                "active": True,
            },
            {
                "code": "balikovna-pickup",
                "name": "Balíkovna – výdejní místo",
                "price": 69,
                "active": True,
            },
        ]

        for data in shipping_data:
            obj, created = ShippingMethod.objects.update_or_create(
                code=data["code"],
                defaults=data
            )
            self.stdout.write(self.style.SUCCESS(
                f"{'Vytvořeno' if created else 'Aktualizováno'}: {obj.name}"
            ))

        self.stdout.write(self.style.SUCCESS("✅ Dopravy úspěšně naplněny."))
