# apps/checkout/forms.py
from django import forms
from decimal import Decimal
from apps.shipping.models import ShippingMethod


# --- Checkout (kontaktní údaje) ---
class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Jméno a příjmení", max_length=150)
    email = forms.EmailField(label="E‑mail")
    phone = forms.CharField(label="Telefon", max_length=40, required=False)
    street = forms.CharField(label="Ulice a číslo", max_length=200)
    city = forms.CharField(label="Město", max_length=120)
    zip_code = forms.CharField(label="PSČ", max_length=20)
    note = forms.CharField(label="Poznámka", widget=forms.Textarea, required=False)


# --- Shipping (doprava/platba) ---
PAYMENT_CHOICES = (
    ("card", "card"),
    ("cod", "cod"),
)


class ShippingForm(forms.Form):
    """
    Robustní formulář pro výběr dopravy/platby.
    Umí přijmout:
      - method (ID ShippingMethod) – (když JS nastaví hidden input), NEBO
      - carrier + režim (balikovna_mode / ppl_mode) a z toho si sám dopočítá ShippingMethod.
    Při pickup-type vyžaduje pickup_point_id/label.
    """

    # primární cesta (když ji nastaví JS)
    method = forms.IntegerField(required=False)

    # fallback bez JS (odvodíme z těchto polí):
    carrier = forms.CharField(required=False)             # 'balikovna' | 'ppl' | 'zasilkovna'
    balikovna_mode = forms.CharField(required=False)      # 'home' | 'pickup'
    ppl_mode = forms.CharField(required=False)            # 'home' | 'pickup'

    # výdejní místo (pro pickup_point)
    pickup_point_id = forms.CharField(required=False)
    pickup_point_label = forms.CharField(required=False)

    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES)

    def _resolve_type(self, carrier: str, bal_mode: str, ppl_mode: str) -> str:
        if carrier == "zasilkovna":
            return ShippingMethod.TYPE_PICKUP
        if carrier == "balikovna":
            return ShippingMethod.TYPE_PICKUP if bal_mode == "pickup" else ShippingMethod.TYPE_HOME
        if carrier == "ppl":
            return ShippingMethod.TYPE_PICKUP if ppl_mode == "pickup" else ShippingMethod.TYPE_HOME
        return ShippingMethod.TYPE_HOME

    def clean(self):
        cleaned = super().clean()
        method_id = cleaned.get("method")
        carrier = (cleaned.get("carrier") or "").strip().lower()
        bal_mode = (cleaned.get("balikovna_mode") or "").strip().lower()
        ppl_mode = (cleaned.get("ppl_mode") or "").strip().lower()
        pay = cleaned.get("payment_method")

        method_obj = None

        # 1) přednostně method_id (nastaveno JS)
        if method_id:
            try:
                method_obj = ShippingMethod.objects.get(id=method_id, active=True)
            except ShippingMethod.DoesNotExist:
                raise forms.ValidationError("Zvolená doprava již není dostupná. Zkuste znovu.")

        # 2) fallback bez JS
        if method_obj is None:
            if not carrier:
                raise forms.ValidationError("Vyberte prosím dopravce.")
            stype = self._resolve_type(carrier, bal_mode, ppl_mode)
            method_obj = (
                ShippingMethod.objects.filter(provider=carrier, type=stype, active=True)
                .order_by("price")
                .first()
            )
            if not method_obj:
                raise forms.ValidationError("Pro zvoleného dopravce teď nemáme dostupnou metodu.")

        # 3) u pickup typu vyžadujeme výdejní místo
        if method_obj.type == ShippingMethod.TYPE_PICKUP:
            if not cleaned.get("pickup_point_id"):
                raise forms.ValidationError("Vyberte prosím výdejní místo.")
            if not cleaned.get("pickup_point_label"):
                cleaned["pickup_point_label"] = f"{method_obj.provider.upper()} {cleaned.get('pickup_point_id')}"

        # 4) dobírka jen tam, kde je podporovaná
        if pay == "cod" and not method_obj.cod_supported:
            raise forms.ValidationError("Zvolená doprava nepodporuje dobírku. Zvolte prosím platbu kartou.")

        cleaned["resolved_method"] = method_obj
        return cleaned

    def get_method(self) -> ShippingMethod:
        return self.cleaned_data.get("resolved_method")
