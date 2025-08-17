import os
import sys

# Cíl: vložit <link rel="stylesheet" href="/static/overrides.css">
# těsně PŘED </head> do Blueberry index.html

INDEX_PATH = os.path.join(
    "templates", "blueberry",
    "Blueberry - eCommerce Tailwind CSS Template",
    "blueberry-tailwind", "index.html"
)

INJECT = '  <link rel="stylesheet" href="/static/overrides.css">\n'

def main():
    if not os.path.isfile(INDEX_PATH):
        print("ERROR: Nenalezl jsem index:", INDEX_PATH)
        sys.exit(1)

    with open(INDEX_PATH, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Pokud už je link vložen, nic neděláme
    if '/static/overrides.css' in html:
        print("Patch: overrides.css už je vložen. Hotovo.")
        return

    lower = html.lower()
    pos = lower.rfind("</head>")
    if pos == -1:
        print("ERROR: V souboru chybí </head>. Patch zrušen.")
        sys.exit(1)

    patched = html[:pos] + INJECT + html[pos:]

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(patched)

    print("Patch hotový: vložen link na /static/overrides.css")

if __name__ == "__main__":
    main()
