# find_author.py
import re

def find():
    with open("scratch/reel.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Look for instagram usernames in the text, e.g. "instagram.com/username"
    # or inside JSON structures: "username":"..."
    usernames = set(re.findall(r'"username":"([^"]+)"', content))
    print("Usernames found in JSON data:")
    for u in usernames:
        print(" -", u)

    # Let's search for matches of any URL pattern with github
    github_urls = set(re.findall(r'github\.com/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+', content, re.IGNORECASE))
    print("\nGitHub URLs found:")
    for g in github_urls:
        print(" -", g)

    # Let's search for "reel" details
    title = re.findall(r'<title>(.*?)</title>', content)
    print("\nTitles found:", title)

if __name__ == "__main__":
    find()
