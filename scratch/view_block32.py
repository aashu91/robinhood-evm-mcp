# view_block32.py
import re

def view():
    with open("scratch/reel2.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if len(script_blocks) > 32:
        block = script_blocks[32]
        print(f"Block 32 length: {len(block)}")
        
        # Let's search for "caption" or "description" and print 500 characters around it
        for match in re.finditer(r'caption', block, re.IGNORECASE):
            pos = match.start()
            print(f"\nMatch 'caption' at position {pos}:")
            print(block[max(0, pos-200):min(len(block), pos+300)])
            print("="*40)
            break # just print the first one

if __name__ == "__main__":
    view()
