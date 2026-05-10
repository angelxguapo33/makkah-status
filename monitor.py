import os
import json
import cv2
import yt_dlp
import google.generativeai as genai
import subprocess
from datetime import datetime

# --- إعداداتك الخاصة ---
API_KEY = "AIzaSyCLjgTgokfmUu2qpNEJ2fYwLQE-5jnhzVU"
REPO_PATH = r"C:\Users\Flores de primavera\Desktop\MakkahBot"
YOUTUBE_URL = "https://www.youtube.com/watch?v=fZvuHkHYaXk"

def main():
    try:
        # 1. إعداد جوجل وتجربة الموديلات المتاحة
        genai.configure(api_key=API_KEY)
        
        # كود ذكي لاختيار الموديل المتاح تلقائياً لتجنب خطأ 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
        print(f"✅ استخدام موديل: {model_name}")
        
        model = genai.GenerativeModel(model_name)

        # 2. جلب البث
        print("🔄 جلب البث المباشر...")
        ydl_opts = {'format': 'best', 'quiet': True, 'cookiefile': 'cookies.txt', 'nocheckcertificate': True}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
        
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret: raise Exception("فشل التقاط الصورة")
        cv2.imwrite("frame.jpg", frame)
        cap.release()

        # 3. التحليل
        img = genai.upload_file(path="frame.jpg")
        response = model.generate_content([img, "Crowd density in Makkah Mataf: Light, Medium, or Heavy? One word only."])
        status = response.text.strip()
        
        # 4. الحفظ والرفع
        res = {"status": status, "time": str(datetime.now())}
        with open("status.json", "w") as f: json.dump(res, f)
        
        os.chdir(REPO_PATH)
        subprocess.run(["git", "add", "status.json"], check=True)
        subprocess.run(["git", "commit", "-m", "update"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"✅ نجحت العملية! الحالة: {status}")

    except Exception as e:
        print(f"❌ خطأ حقيقي: {e}")

if __name__ == "__main__":
    main()
