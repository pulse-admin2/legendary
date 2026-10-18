import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# توکن به صورت مخفی از تنظیمات رندر خوانده می‌شود تا در گیت‌هاب عمومی لو نرود
TOKEN = os.getenv("S_TOKEN")
BASE_URL = f"https://splus.ir{TOKEN}"

def send_message(to_id, text):
    """تابع اصلی ارسال پیام به کاربران یا گروه‌ها"""
    url = f"{BASE_URL}/sendMessage"
    payload = {"to": to_id, "type": "TEXT", "body": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error sending message:", e)

@app.get("/")
def home():
    return {"status": "Pulse Bot is running active!"}

@app.post("/webhook")
async def webhook(request: Request):
    """دریافت زنده پیام‌ها از سرور سروش پلاس"""
    try:
        data = await request.json()
        if "messages" in data:
            for message in data["messages"]:
                chat_id = message.get("from")  # آیدی گروه یا کاربر فرستنده
                text = message.get("body", "").strip()
                
                if not chat_id or not text:
                    continue

                # تشخیص پیام‌های ارسالی از گروه (آیدی گروه در سروش معمولاً با g شروع می‌شود)
                is_group = chat_id.startswith("g")

                # 🛠 دستورات اولیه ربات پالس
                if text == "/start":
                    send_message(chat_id, "سلام! به ربات مدیریت و پشتیبانی پالس خوش آمدید. ⚡")
                
                elif text == "/setup" and is_group:
                    send_message(chat_id, "⚙️ ربات پالس در این گروه فعال شد و آماده پیکربندی است.")

                elif text.startswith("/ban ") and is_group:
                    user_to_ban = text.replace("/ban ", "")
                    send_message(chat_id, f"❌ کاربر {user_to_ban} به دستور مدیریت اخراج شد.")
                    
    except Exception as e:
        print("Error in webhook:", e)

    return {"status": "ok"}
  
