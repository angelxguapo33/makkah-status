import os
import json
import subprocess
from google import genai
from datetime import datetime

API_KEY = os.getenv("GEMINI_KEY")

# الرابط الخاص بك
DIRECT_STREAM_URL = "https://live.kwikmotion.com/ksaquranlive/ksaquran.smil/ksaquranpublish/ksaquran_source/hdntl=exp=1778515953~acl=%2fksaquranlive%2fksaquran.smil%2f*~data=hdntl~hmac=5667c54e49514dd4a45a5c37ad1290f643afbb56916240ad6502d48e6506df09/chunks_dvr.m3u8"

def main():
    print("--- بدء التحديث السحابي المباشر عبر FFmpeg ---")
    try:
        if not API_KEY: raise Exception("Missing GEMINI_KEY")
        client = genai.Client(api_key=API_KEY)
        
        print("جاري سحب الصورة وتخطي الحماية...")
        
        # أمر FFmpeg السري للتنكر كمتصفح قادم من الموقع الرسمي
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            '-headers', 'Referer: https://aloula.sba.sa/\r\n',
            '-i', DIRECT_STREAM_URL,
            '-vframes', '1',
            '-q:v', '2',
            'frame.jpg'
        ]
        
        # تشغيل الأمر في السيرفر
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        # التحقق من نجاح التقاط الصورة
        if not os.path.exists("frame.jpg"):
            print("تفاصيل الخطأ من السيرفر:\n", result.stderr)
            raise Exception("السيرفر رفض الرابط. قد يكون الرابط مقفلاً برقم IP الخاص بحاسوبك (IP-Bound) ولا يعمل على السيرفرات السحابية.")
            
        print("تم التقاط الصورة بنجاح.")

        print("جاري التحليل...")
        with open("frame.jpg", "rb") as f:
            image_bytes = f.read()
            
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=["Analyze crowd density in the Makkah Mataf area from this image. Reply with only one word: Light, Medium, or Heavy.", image_bytes]
        )
        
        status_result = response.text.strip()
        
        data = {
            "status": status_result,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ تمت العملية بنجاح! الحالة: {status_result}")

    except Exception as e:
        print(f"❌ خطأ فني: {str(e)}")
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump({"status": "Token/IP Blocked", "last_update": str(datetime.now())}, f)
        exit(1)

if __name__ == "__main__":
    main()
