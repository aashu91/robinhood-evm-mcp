# print_meta_tags.py
import re
import html

def print_meta():
    with open("scratch/reel2.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    meta_tags = re.findall(r'<meta[^>]*>', content, re.IGNORECASE)
    print(f"Found {len(meta_tags)} meta tags:")
    for idx, mt in enumerate(meta_tags):
        print(f"{idx}: {html.unescape(mt)}")

if __name__ == "__main__":
    print_meta()
