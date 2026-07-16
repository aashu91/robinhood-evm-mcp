# parse_json_reel2.py
import re
import json

def parse():
    with open("scratch/reel2.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Find all <script> blocks
    script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    print(f"Found {len(script_blocks)} script blocks.")

    # Search for description keywords or shortcode
    for idx, sb in enumerate(script_blocks):
        if "edge_media_to_caption" in sb or "accessibility_caption" in sb or "shortcode" in sb or "owner" in sb:
            print(f"\nBlock {idx} contains interesting keywords!")
            # Try to print some text matches or extract JSON
            # Let's extract substrings that look like captions
            captions = re.findall(r'"text"\s*:\s*"([^"]+)"', sb)
            if captions:
                print("Found text values:")
                for cap in captions[:10]:
                    if len(cap.strip()) > 10:
                        print(" -", cap[:150])
            
            # Let's find any URLs
            urls = re.findall(r'https?://[^\s"\'\\<>]+', sb)
            if urls:
                print("Found URLs:")
                for url in urls[:10]:
                    print(" -", url)

if __name__ == "__main__":
    parse()
