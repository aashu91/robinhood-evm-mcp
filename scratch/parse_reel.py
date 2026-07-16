# parse_reel.py
import re
import html

def parse():
    with open("scratch/reel.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Find title
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    if title_match:
        print("TITLE:", html.unescape(title_match.group(1)))

    # Find meta description or caption-like structures
    meta_desc = re.findall(r'<meta\s+name="description"\s+content="(.*?)"', content, re.IGNORECASE)
    for md in meta_desc:
        print("META DESCRIPTION:", html.unescape(md))

    og_title = re.findall(r'<meta\s+property="og:title"\s+content="(.*?)"', content, re.IGNORECASE)
    for ot in og_title:
        print("OG TITLE:", html.unescape(ot))

    og_desc = re.findall(r'<meta\s+property="og:description"\s+content="(.*?)"', content, re.IGNORECASE)
    for od in og_desc:
        print("OG DESCRIPTION:", html.unescape(od))

    # Let's search for "github" anywhere in the file (contextual search)
    # Find lines or text around "github"
    github_matches = re.findall(r'(.{0,100}github.{0,100})', content, re.IGNORECASE)
    if github_matches:
        print("\nGITHUB MATCHES:")
        for idx, match in enumerate(github_matches[:10]):
            print(f"{idx}: {match.strip()}")

if __name__ == "__main__":
    parse()
