import os
import json
import cv2
import yt_dlp
import google.generativeai as genai
from datetime import datetime

# استلام المفتاح من نظام GitHub (الـ Secrets)
API_KEY = "AIzaSyCLjgTgokfmUu2qpNEJ2fYwLQE-5jnhzVU"
YOUTUBE_URL = "https://www.youtube.com/watch?v=fZvuHkHYaXk"

def main():
    try:
        if not API_KEY:
            raise Exception("المفتاح السري GEMINI_KEY غير موجود في إعدادات GitHub!")

        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # استخدام ملف الكوكيز الذي سيتم إنشاؤه تلقائياً في السيرفر
        ydl_opts = {'format': 'best', 'quiet': True, 'cookiefile': 'cookies.txt'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
        
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret: raise Exception("فشل سحب البث")
        cv2.imwrite("frame.jpg", frame)
        cap.release()

        # التحليل عبر Gemini
        img = genai.upload_file(path="frame.jpg")
        response = model.generate_content([img, "Crowd density: Light, Medium, or Heavy? One word only."])
        
        # حفظ النتيجة في مسار السيرفر (بدون C:\Users)
        res = {"status": response.text.strip(), "last_update": str(datetime.now())}
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False)
            
        print(f"✅ الحالة الحالية: {res['status']}")

    except Exception as e:
        print(f"❌ خطأ تقني: {e}")

if __name__ == "__main__":
    main()
