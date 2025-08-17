import os
import zipfile
import shutil
import sys

"""
Usage:
  python scripts/import_blueberry.py "C:/path/to/Blueberry - eCommerce Tailwind CSS Template.zip"

This will extract HTML files into templates/blueberry and all other assets into static/blueberry.
"""

def main():
    if len(sys.argv) < 2:
        print("ERROR: Provide path to the Blueberry ZIP.")
        sys.exit(1)

    src_zip = sys.argv[1]
    if not os.path.isfile(src_zip):
        print("ERROR: ZIP not found:", src_zip)
        sys.exit(1)

    extract_dir = ".blueberry_tmp_extract"
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(src_zip, "r") as z:
        z.extractall(extract_dir)

    # Destination folders
    tpl_dst = os.path.join("templates", "blueberry")
    st_dst = os.path.join("static", "blueberry")
    os.makedirs(tpl_dst, exist_ok=True)
    os.makedirs(st_dst, exist_ok=True)

    count_html = 0
    count_other = 0

    # Heuristic copy: .html -> templates; others -> static
    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, extract_dir)
            ext = os.path.splitext(f)[1].lower()
            if ext in [".html", ".htm"]:
                dst = os.path.join(tpl_dst, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                count_html += 1
            else:
                dst = os.path.join(st_dst, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                count_other += 1

    shutil.rmtree(extract_dir, ignore_errors=True)
    print(f"Imported: {count_html} HTML files -> templates/blueberry, {count_other} assets -> static/blueberry")
    print("Done. You can now run: python manage.py runserver")

if __name__ == "__main__":
    main()
