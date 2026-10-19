import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN = os.getenv("S_TOKEN")
BASE_URL = f"https://splus.ir{TOKEN}"

def send_message(to_id, text):
    """تابع ارسال پیام متنی"""
    url = f"{BASE_URL}/sendMessage"
    payload = {"to": to_id, "type": "TEXT", "body": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error sending message:", e)

def join_group_by_link(link):
    """تابع ویژه برای ورود ربات به گروه از طریق لینک دعوت"""
    url = f"{BASE_URL}/joinGroup"
    # استخراج هش یا شناسه لینک دعوت از انتهای آدرس
    invite_token = link.split("/")[-1]
    payload = {"inviteToken": invite_token}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("success"):
                return True, res_data.get("group_id")
        return False, None
    except Exception as e:
        print("Error joining group:", e)
        return False, None

@app.get("/")
def home():
    return {"status": "Pulse Bot is active and running!"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        if "messages" in data:
            for message in data["messages"]:
                chat_id = message.get("from")
                text = message.get("body", "").strip()
                
                if not chat_id or not text:
                    continue

                is_group = chat_id.startswith("g")

                # 🛑 بخش دستورات داخل گروه
                if is_group:
                    if text == "/start" or text == "/setup":
                        send_message(chat_id, "⚡ ربات پالس با موفقیت از طریق لینک وارد این گروه شد و آماده مدیریت است!")
                    
                    elif text.startswith("/ban "):
                        user_to_ban = text.replace("/ban ", "")
                        send_message(chat_id, f"❌ کاربر {user_to_ban} با موفقیت اخراج شد.")

                # 🛑 بخش دستورات پی‌وی ربات (پشتیبانی و ورود به گروه)
                else:
                    if text == "/start":
                        send_message(chat_id, "سلام ادمین گرامی! ⚡\nبرای اینکه من را عضو گروه کنی، لطفاً لینک دعوت گروه را به این صورت ارسال کن:\n\n/join https://splus.ir...")
                    
                    elif text.startswith("/join "):
                        group_link = text.replace("/join ", "").strip()
                        if "splus.ir/joingroup/" in group_link:
                            send_message(chat_id, "⏳ در حال تلاش برای ورود به گروه...")
                            success, g_id = join_group_by_link(group_link)
                            if success:
                                send_message(chat_id, f"✅ با موفقیت وارد گروه شدم!\nشناسه گروه: {g_id}\n\n⚠️ لطفاً همین حالا در گروه من را ادمین (مدیر) کنید تا بتوانم فعالیتم را شروع کنم.")
                                # ارسال پیام خوش‌آمدگویی اولیه به گروه جدید
                                send_message(g_id, "سلام به همگی! من ربات مدیریت پالس هستم. لطفا من را ادمین کنید. ⚙️")
                            else:
                                send_message(chat_id, "❌ خطایی رخ داد. مطمئن شوید لینک دعوت معتبر و منقضی نشده باشد.")
                        else:
                            send_message(chat_id, "❌ فرمت لینک ارسالی اشتباه است. لینک باید مربوط به سروش پلاس باشد.")
                            
    except Exception as e:
        print("Error in webhook:", e)

    return {"status": "ok"}
                                
