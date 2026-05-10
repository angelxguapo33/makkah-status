import os
import json
import cv2
import yt_dlp
import google.generativeai as genai
from datetime import datetime

# 1. جلب المفتاح السري من نظام GitHub (هذا هو الأصح والآمن)
API_KEY = os.getenv("GEMINI_KEY")
YOUTUBE_URL = "https://www.youtube.com/watch?v=fZvuHkHYaXk"

def main():
    print("--- بدء عملية التحديث السحابي ---")
    
    try:
        # التحقق من أن المفتاح وصل للكود من السيرفر
        if not API_KEY:
            raise Exception("خطأ: لم يتم العثور على GEMINI_KEY في إعدادات GitHub Secrets!")

        # 2. إعداد جيمناي
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 3. إعدادات تجاوز حظر يوتيوب (ضرورية جداً)
        print("جاري الاتصال بالبث المباشر...")
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            'nocheckcertificate': True,
            # إضافة هوية متصفح لخداع يوتيوب
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
        
        # 4. التقاط الصورة
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret:
            raise Exception("فشل التقاط صورة (يوتيوب حظر الـ IP الخاص بالسيرفر)")
        
        image_path = "frame.jpg"
        cv2.imwrite(image_path, frame)
        cap.release()
        print("تم التقاط الصورة بنجاح.")

        # 5. تحليل الصورة
        print("جاري تحليل الزحام...")
        raw_image = genai.upload_file(path=image_path)
        prompt = "Analyze the crowd density in the Makkah Mataf area. Reply with only one word: Light, Medium, or Heavy."
        response = model.generate_content([raw_image, prompt])
        
        status_result = response.text.strip()
        print(f"النتيجة: {status_result}")

        # 6. كتابة البيانات في ملف status.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "status.json")
        
        data_to_save = {
            "status": status_result,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        
        print(f"✅ تم التحديث بنجاح: {status_result}")

    except Exception as e:
        print(f"❌ حدث خطأ فني: {str(e)}")
        # كتابة الخطأ في الملف ليظهر في بلوجر
        with open("status.json", "w") as f:
            json.dump({"status": f"Error: {str(e)}", "last_update": str(datetime.now())}, f)
        exit(1)

if __name__ == "__main__":
    main()
