# analyze_video.py
import os
import time
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv("/data/data/com.termux/files/home/.env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env")
    exit(1)

video_path = "/sdcard/Download/Video-416.mp4"
if not os.path.exists(video_path):
    # Try backup path
    video_path = "/storage/emulated/0/Download/Video-416.mp4"
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found at /sdcard/Download/Video-416.mp4")
        exit(1)

file_size = os.path.getsize(video_path)
print(f"Uploading {video_path} ({file_size / (1024*1024):.2f} MB) to Gemini File API...")

# Step 1: Start Resumable Upload Session
url_start = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}"
headers_start = {
    "X-Goog-Upload-Protocol": "resumable",
    "X-Goog-Upload-Command": "start",
    "X-Goog-Upload-Header-Content-Length": str(file_size),
    "X-Goog-Upload-Header-Content-Type": "video/mp4",
    "Content-Type": "application/json"
}
body_start = {
    "file": {
        "display_name": "Video-416.mp4"
    }
}

try:
    res_start = requests.post(url_start, headers=headers_start, json=body_start)
    res_start.raise_for_status()
    upload_url = res_start.headers.get("X-Goog-Upload-URL")
    if not upload_url:
        print("❌ Error: Failed to retrieve upload URL from response.")
        exit(1)
    print("✅ Upload session started.")
except Exception as e:
    print(f"❌ Error initiating upload: {e}")
    exit(1)

# Step 2: Upload file contents
headers_upload = {
    "X-Goog-Upload-Offset": "0",
    "X-Goog-Upload-Command": "upload, finalize",
    "Content-Length": str(file_size),
    "Content-Type": "video/mp4"
}

try:
    with open(video_path, "rb") as f:
        file_data = f.read()
    res_upload = requests.post(upload_url, headers=headers_upload, data=file_data)
    res_upload.raise_for_status()
    upload_result = res_upload.json()
    file_uri = upload_result.get("file", {}).get("uri")
    file_name = upload_result.get("file", {}).get("name")
    print(f"✅ Upload completed. File URI: {file_uri}, Name: {file_name}")
except Exception as e:
    print(f"❌ Error uploading file data: {e}")
    exit(1)

# Step 3: Wait for file processing to complete
print("Waiting for file to be processed by Gemini (status -> ACTIVE)...")
url_get = f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={api_key}"
status = "PROCESSING"
while status == "PROCESSING":
    try:
        res_get = requests.get(url_get)
        res_get.raise_for_status()
        file_info = res_get.json()
        status = file_info.get("state", "PROCESSING")
        print(f"  Current state: {status}")
        if status == "ACTIVE":
            break
        elif status == "FAILED":
            print("❌ File processing failed on Gemini side.")
            exit(1)
    except Exception as e:
        print(f"⚠️ Error checking file status: {e}")
    time.sleep(5)

# Step 4: Generate Content
print("\nGenerating description and transcribing video content...")
url_generate = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
body_generate = {
    "contents": [
        {
            "parts": [
                {
                    "file_data": {
                        "mime_type": "video/mp4",
                        "file_uri": file_uri
                    }
                },
                {
                    "text": "Analyze this video in detail. Describe what is being shown in the video step-by-step, transcribe all spoken words (Hindi/English), and list any code, websites, github repos, UI designs, or text that is shown on the screen. Summarize the main instructions or requests of this video clearly."
                }
            ]
        }
    ]
}

try:
    res_generate = requests.post(url_generate, json=body_generate)
    res_generate.raise_for_status()
    gen_result = res_generate.json()
    
    text_output = gen_result["candidates"][0]["content"]["parts"][0]["text"]
    print("\n" + "="*50)
    print("🎥 GEMINI ANALYSIS RESULT:")
    print("="*50)
    print(text_output)
    print("="*50)
except Exception as e:
    print(f"❌ Error generating content: {e}")
    if 'res_generate' in locals():
        print(res_generate.text)
