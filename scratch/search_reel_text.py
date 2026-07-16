# search_reel_text.py
import re

def search():
    with open("scratch/reel.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    keywords = ["github", "scroll", "three", "canvas", "portal", "diorama", "3d", "website", "code"]
    print(f"File size: {len(content)} characters.")

    for kw in keywords:
        matches = [m.start() for m in re.finditer(kw, content, re.IGNORECASE)]
        print(f"\nKeyword '{kw}': {len(matches)} matches")
        for idx, pos in enumerate(matches[:5]):
            start = max(0, pos - 100)
            end = min(len(content), pos + 100)
            snippet = content[start:end].replace('\n', ' ').strip()
            print(f"  Match {idx}: ... {snippet} ...")

if __name__ == "__main__":
    search()
