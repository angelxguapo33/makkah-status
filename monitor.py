import os
import json
import cv2
import yt_dlp
from google import genai # المكتبة الجديدة
from datetime import datetime

# استلام المفتاح
API_KEY = os.getenv("GEMINI_KEY")
YOUTUBE_URL = "https://www.youtube.com/watch?v=fZvuHkHYaXk"

def main():
    print("--- بدء التحديث باستخدام تقنيات 2026 ---")
    try:
        if not API_KEY: raise Exception("Missing GEMINI_KEY")

        # 1. إعداد العميل الجديد لجيمناي
        client = genai.Client(api_key=API_KEY)
        
        # 2. جلب البث مع حل تحدي يوتيوب (n-challenge)
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            'nocheckcertificate': True,
            # إجبار السيرفر على محاكاة متصفح حقيقي جداً
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("جاري فك تشفير رابط يوتيوب...")
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
        
        # 3. سحب الصورة
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret: raise Exception("يوتيوب حظر الاتصال بالبث")
        
        cv2.imwrite("frame.jpg", frame)
        cap.release()

        # 4. تحليل الصورة (بالطريقة الجديدة)
        print("جاري التحليل...")
        with open("frame.jpg", "rb") as f:
            image_bytes = f.read()
            
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=["Analyze crowd density in Makkah. Reply only: Light, Medium, or Heavy.", image_bytes]
        )
        
        status_result = response.text.strip()

        # 5. حفظ النتيجة
        data = {
            "status": status_result,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ تم بنجاح: {status_result}")

    except Exception as e:
        print(f"❌ خطأ فني: {str(e)}")
        # إذا استمر الحظر، سنعرف فوراً في بلوجر
        with open("status.json", "w") as f:
            json.dump({"status": "YouTube Security Active", "last_update": str(datetime.now())}, f)
        exit(1)

if __name__ == "__main__":
    main()
