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
    print("--- بدء عملية التحديث السحابي ---")
    
    try:
        # التحقق من وجود المفتاح
        if not API_KEY:
            raise Exception("خطأ: لم يتم العثور على GEMINI_KEY في Secrets!")

        # 2. إعداد جيمناي
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 3. جلب البث المباشر باستخدام الكوكيز
        print("جاري الاتصال بالبث المباشر...")
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            'nocheckcertificate': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
        
        # 4. التقاط الصورة
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret:
            raise Exception("فشل التقاط صورة من البث المباشر")
        
        image_path = "frame.jpg"
        cv2.imwrite(image_path, frame)
        cap.release()
        print("تم التقاط الصورة بنجاح.")

        # 5. تحليل الصورة عبر الذكاء الاصطناعي
        print("جاري تحليل الزحام عبر Gemini...")
        raw_image = genai.upload_file(path=image_path)
        prompt = "Analyze the crowd density in the Makkah Mataf area from this image. Reply with only one word: Light, Medium, or Heavy."
        response = model.generate_content([raw_image, prompt])
        
        status_result = response.text.strip()
        print(f"النتيجة المستخلصة: {status_result}")

        # 6. كتابة البيانات في ملف status.json (إجباري)
        # نستخدم المسار المطلق لضمان الكتابة في بيئة Linux
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "status.json")
        
        data_to_save = {
            "status": status_result,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        
        print(f"✅ تم تحديث ملف status.json بنجاح في المسار: {file_path}")

    except Exception as e:
        # في حال حدوث خطأ، نقوم بطباعته بوضوح في الـ Logs
        print(f"❌ حدث خطأ فني: {str(e)}")
        # نكتب الخطأ في الملف أيضاً لكي تراه في بلوجر وتعرف العطل
        error_data = {"status": f"Error: {str(e)}", "last_update": str(datetime.now())}
        with open("status.json", "w") as f:
            json.dump(error_data, f)
        exit(1) # إجبار الأكشن على إظهار علامة حمراء في حال الفشل

if __name__ == "__main__":
    main()
