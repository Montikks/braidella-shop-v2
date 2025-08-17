# Braidella (F1) — Skeleton + šablona Blueberry

**Datum:** 2025-08-08

Tato verze obsahuje:
- Django 5 skeleton (apps/*), konfigurace settings (base/dev/prod)
- Zaintegrované statické soubory šablony **Blueberry** ve `static/blueberry`
- HTML z šablony ve `templates/blueberry` + dočasná homepage `/` na `blueberry/index.html`
- Dev DB = SQLite, Prod = `DATABASE_URL` (PostgreSQL)
- E-maily v dev do konzole
- Placeholdery pro GoPay v settings
- CZ locale, Europe/Prague

## Lokální běh (PyCharm / terminal)
1. Vytvoř a aktivuj virtuální prostředí (Python 3.12+).
2. Nainstaluj závislosti:
   ```bash
   pip install -r requirements.txt
   ```
3. Vytvoř `.env` podle `.env.example` (alespoň SECRET_KEY).
4. Migrace a start:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
5. Otevři `http://127.0.0.1:8000/` — uvidíš šablonu Blueberry.

## Struktura
- `apps/…` — připravené app složky pro další fáze
- `config/settings/…` — `base.py`, `dev.py`, `prod.py`
- `templates/blueberry/…` — HTML stránky šablony
- `static/blueberry/…` — CSS/JS/obrázky šablony

## Další fáze
- F1b: Převést header/footer do `base.html` a rozsekat na partialy (Tailwind)
- F2+: Checkout, dopravy/platby, pickery, e-maily
