import os
import json
import cv2
from google import genai
from datetime import datetime

API_KEY = os.getenv("GEMINI_KEY")

# الرابط الخاص بك الذي قمت باستخراجه
DIRECT_STREAM_URL = "https://live.kwikmotion.com/ksaquranlive/ksaquran.smil/ksaquranpublish/ksaquran_source/hdntl=exp=1778515953~acl=%2fksaquranlive%2fksaquran.smil%2f*~data=hdntl~hmac=5667c54e49514dd4a45a5c37ad1290f643afbb56916240ad6502d48e6506df09/chunks_dvr.m3u8"

def main():
    print("--- بدء التحديث المباشر السريع ---")
    try:
        if not API_KEY: raise Exception("Missing GEMINI_KEY")

        client = genai.Client(api_key=API_KEY)
        
        print("جاري التقاط الصورة من البث المباشر...")
        cap = cv2.VideoCapture(DIRECT_STREAM_URL)
        ret, frame = cap.read()
        
        if not ret: 
            raise Exception("فشل التقاط الصورة. (إذا ظهر هذا الخطأ لاحقاً، فهذا يعني أن الرابط انتهت صلاحيته ويجب جلب واحد جديد)")
        
        cv2.imwrite("frame.jpg", frame)
        cap.release()
        print("تم التقاط الصورة بنجاح.")

        print("جاري تحليل الزحام...")
        with open("frame.jpg", "rb") as f:
            image_bytes = f.read()
            
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=["Analyze crowd density in the Makkah Mataf area from this image. Reply with only one word: Light, Medium, or Heavy.", image_bytes]
        )
        
        status_result = response.text.strip()

        # حفظ البيانات
        data = {
            "status": status_result,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ تمت العملية بنجاح! الحالة: {status_result}")

    except Exception as e:
        print(f"❌ خطأ فني: {str(e)}")
        with open("status.json", "w") as f:
            json.dump({"status": "Stream Error", "last_update": str(datetime.now())}, f)
        exit(1)

if __name__ == "__main__":
    main()
