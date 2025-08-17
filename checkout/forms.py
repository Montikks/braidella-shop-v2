from django import forms
import re

ZIP_RE = re.compile(r"^\d{3}\s?\d{2}$")
PHONE_RE = re.compile(r"^\+?[\d\s]{9,15}$")

# Přidáváme třetí možnost dopravy – PPL Parcelshop.
DELIVERY_CHOICES = [
    ("address", "Doručení na adresu"),
    ("balikovna", "Balíkovna (výdejní místo)"),
    ("ppl", "PPL Parcelshop (výdejní místo)"),
]

class AddressForm(forms.Form):
    # povinné
    first_name = forms.CharField(label="Jméno", max_length=60)
    last_name = forms.CharField(label="Příjmení", max_length=60)
    email = forms.EmailField(label="E-mail", max_length=120)
    phone = forms.CharField(label="Telefon", max_length=20, help_text="Např. +420 123 456 789")

    # doprava
    delivery_method = forms.ChoiceField(
        label="Způsob doručení",
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect
    )

    # adresa
    street = forms.CharField(label="Ulice a č.p.", max_length=120, required=False)
    city = forms.CharField(label="Město", max_length=80, required=False)
    zip_code = forms.CharField(label="PSČ", max_length=10, required=False, help_text="Např. 110 00")

    # Balíkovna
    balikovna_id = forms.CharField(  # čitelné shrnutí (název, ZIP, adresa)
        label="Výdejní místo Balíkovny (ID/adresa)",
        max_length=255,  # zvětšeno, ale stejně budeme skládat krátce
        required=False,
        help_text="Vyberete na mapě (nebo zadejte stručně ručně)."
    )
    balikovna_code = forms.CharField(  # skutečné ID pobočky, např. B39207
        label="Kód Balíkovny",
        max_length=32,
        required=False
    )

    # PPL parcelshop – čitelné shrnutí (název, ZIP, adresa)
    ppl_id = forms.CharField(
        label="Výdejní místo PPL (ID/adresa)",
        max_length=255,
        required=False,
        help_text="Vyberete na mapě (nebo zadejte stručně ručně)."
    )
    # PPL parcelshop – skutečný identifikátor pobočky
    ppl_code = forms.CharField(
        label="Kód PPL výdejny",
        max_length=32,
        required=False
    )

    def clean_zip_code(self):
        z = (self.cleaned_data.get("zip_code") or "").strip()
        if not z:
            return z
        if not ZIP_RE.match(z):
            raise forms.ValidationError("Zadej PSČ ve tvaru 110 00.")
        return z

    def clean_phone(self):
        p = (self.cleaned_data.get("phone") or "").strip()
        if not PHONE_RE.match(p):
            raise forms.ValidationError("Zadej platné telefonní číslo (může být s +420).")
        return p

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("delivery_method")
        if method == "address":
            # adresa – požadujeme street, city a zip_code
            for f in ("street", "city", "zip_code"):
                if not (cleaned.get(f) or "").strip():
                    self.add_error(f, "Toto pole je povinné pro doručení na adresu.")
            # nulujeme výdejní místa
            cleaned["balikovna_id"] = ""
            cleaned["balikovna_code"] = ""
            cleaned["ppl_id"] = ""
            cleaned["ppl_code"] = ""
        elif method == "balikovna":
            # u Balíkovny vyžadujeme alespoň code; nulujeme PPL a adresu
            if not (cleaned.get("balikovna_code") or "").strip():
                self.add_error("balikovna_id", "Vyberte Balíkovnu tlačítkem „Vybrat na mapě“.")
            cleaned["street"] = ""
            cleaned["city"] = ""
            cleaned["zip_code"] = ""
            cleaned["ppl_id"] = ""
            cleaned["ppl_code"] = ""
        elif method == "ppl":
            # u PPL vyžadujeme alespoň code; nulujeme Balíkovnu a adresu
            if not (cleaned.get("ppl_code") or "").strip():
                self.add_error("ppl_id", "Vyberte PPL výdejnu tlačítkem „Vybrat na mapě“. ")
            cleaned["street"] = ""
            cleaned["city"] = ""
            cleaned["zip_code"] = ""
            cleaned["balikovna_id"] = ""
            cleaned["balikovna_code"] = ""
        return cleaned
