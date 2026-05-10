import os
import json
import cv2
import yt_dlp
import google.generativeai as genai
from datetime import datetime

# سحب المفتاح من نظام GitHub Secrets
API_KEY = "AIzaSyCLjgTgokfmUu2qpNEJ2fYwLQE-5jnhzVU"
YOUTUBE_URL = "https://www.youtube.com/watch?v=fZvuHkHYaXk"

def main():
    try:
        if not API_KEY: raise Exception("GEMINI_KEY is missing")
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # جلب البث باستخدام الكوكيز
        ydl_opts = {'format': 'best', 'quiet': True, 'cookiefile': 'cookies.txt', 'nocheckcertificate': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
        
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret: raise Exception("Failed to grab frame")
        cv2.imwrite("frame.jpg", frame)
        cap.release()

        # التحليل
        img = genai.upload_file(path="frame.jpg")
        response = model.generate_content([img, "Crowd density: Light, Medium, or Heavy? One word only."])
        
        res = {"status": response.text.strip(), "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=4)
        print(f"Success: {res['status']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
