# find_caption_json.py
import re

def find():
    with open("scratch/reel2.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    
    # Search for "node" or "edges" or "text" or "caption" in all script blocks
    for idx, block in enumerate(script_blocks):
        if len(block) > 5000:
            # Look for "edge_media_to_caption"
            if "edge_media_to_caption" in block:
                print(f"Block {idx} contains edge_media_to_caption! Length: {len(block)}")
                # Find all occurrences of "text" within this block
                text_matches = re.finditer(r'"text"\s*:\s*"([^"]+)"', block)
                for tm in text_matches:
                    text_val = tm.group(1)
                    if len(text_val) > 20:
                        print("  Found Text:", text_val[:200])

            # Also look for any direct text containing "github" or "http"
            if "github" in block.lower():
                print(f"Block {idx} contains 'github'! Length: {len(block)}")
                matches = re.finditer(r'github', block, re.IGNORECASE)
                for m in matches:
                    pos = m.start()
                    print("  Snippet:", block[max(0, pos-100):min(len(block), pos+100)].strip())

if __name__ == "__main__":
    find()
