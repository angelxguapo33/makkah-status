import os
import json
import cv2
import yt_dlp
from google import genai
from datetime import datetime

API_KEY = os.getenv("GEMINI_KEY")
YOUTUBE_URL = "https://www.youtube.com/watch?v=fZvuHkHYaXk"

def main():
    print("--- محاولة فك التشفير باستخدام محرك Node.js ---")
    try:
        if not API_KEY: raise Exception("Missing GEMINI_KEY")

        client = genai.Client(api_key=API_KEY)
        
        # إعدادات نظيفة تعتمد على الكوكيز وحل الجافا سكريبت
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            # تمت إزالة سطر الأندرويد الذي تسبب في التعارض
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("جاري استخراج الرابط وتخطي اللغز...")
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
        
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret: raise Exception("تم تجاوز اللغز ولكن يوتيوب يرفض تسليم إطارات البث (حظر IP).")
        
        cv2.imwrite("frame.jpg", frame)
        cap.release()

        print("جاري التحليل...")
        with open("frame.jpg", "rb") as f:
            image_bytes = f.read()
            
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=["Analyze crowd density in Makkah. Reply only: Light, Medium, or Heavy.", image_bytes]
        )
        
        status_result = response.text.strip()

        data = {
            "status": status_result,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ تمت العملية بنجاح: {status_result}")

    except Exception as e:
        print(f"❌ خطأ فني: {str(e)}")
        with open("status.json", "w") as f:
            json.dump({"status": "YouTube Security Active", "last_update": str(datetime.now())}, f)
        exit(1)

if __name__ == "__main__":
    main()
