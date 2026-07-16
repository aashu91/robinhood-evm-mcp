# fetch_reel_v2.py
import os
import json
import instaloader

def fetch_post(shortcode):
    L = instaloader.Instaloader()
    L.download_pictures = False
    L.download_videos = False
    L.download_comments = False
    L.save_metadata = False

    cookies_path = "/data/data/com.termux/files/home/.instagram_cookies.json"
    netscape_path = "/data/data/com.termux/files/home/instagram_cookies.txt"

    loaded = False
    target_path = cookies_path
    if os.path.exists(target_path):
        loaded = True
    elif os.path.exists(netscape_path):
        target_path = netscape_path
        loaded = True

    if loaded:
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content.startswith("["):
                cookie_list = json.loads(content)
                for cookie in cookie_list:
                    name = cookie.get("name")
                    value = cookie.get("value")
                    domain = cookie.get("domain", "")
                    path = cookie.get("path", "/")
                    if "instagram.com" not in domain:
                        continue
                    L.context._session.cookies.set(name, value, domain=domain, path=path)
            else:
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) == 7:
                        domain, _, path, _, _, name, value = parts
                        if "instagram.com" not in domain:
                            continue
                        L.context._session.cookies.set(name, value, domain=domain, path=path)
            print("Session cookies loaded.")
        except Exception as e:
            print(f"Error loading cookies: {e}")

    try:
        print(f"Fetching post metadata for shortcode: {shortcode}...")
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print("\n=== REEL CAPTION ===")
        print(post.caption)
        print("====================")
    except Exception as e:
        print(f"Error fetching post: {e}")

if __name__ == "__main__":
    fetch_post("DayIBJ1M430")
