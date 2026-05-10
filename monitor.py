import os
import json
import cv2
import yt_dlp
import google.generativeai as genai

# جلب المفتاح السري
API_KEY = os.environ.get("GEMINI_API_KEY")
YOUTUBE_URL = "https://www.youtube.com/channel/UCos52azQNBgW63_9uDJoPDA/live"

def save_status(status_text):
    with open("status.json", "w", encoding="utf-8") as f:
        json.dump({"status": status_text}, f, ensure_ascii=False)

def main():
    if not API_KEY:
        save_status("Error: No API Key")
        return
    
    # 1. التمويه الاحترافي: التنكر كتطبيق أندرويد لتجاوز حظر الروبوتات
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'client': ['android', 'mweb']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            stream_url = info['url']
    except Exception as e:
        save_status(f"YT Error: {str(e)[:50]}")
        return

    # 2. التقاط صورة من البث
    try:
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        if not ret:
            save_status("Error: Capture Frame")
            return
        cv2.imwrite("frame.jpg", frame)
        cap.release()
    except Exception as e:
        save_status(f"CV Error: {str(e)[:50]}")
        return

    # 3. التحليل بالذكاء الاصطناعي
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        Analyze this image of the Holy Mosque in Makkah. 
        Classify the crowd density in the Mataf area into one of three levels only: 
        Light, Medium, or Heavy. 
        Respond with only ONE WORD in English.
        """
        image_file = genai.upload_file(path="frame.jpg")
        response = model.generate_content([image_file, prompt])
        result = response.text.strip()
        
        # التأكد من صحة النتيجة
        if "Heavy" in result:
            final_status = "Heavy"
        elif "Medium" in result:
            final_status = "Medium"
        elif "Light" in result:
            final_status = "Light"
        else:
            final_status = "Wait"
            
        save_status(final_status)
    except Exception as e:
        save_status(f"AI Error: {str(e)[:50]}")

if __name__ == "__main__":
    main()
