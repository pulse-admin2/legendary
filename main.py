import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# ۱. دریافت توکن از تنظیمات رندر
TOKEN = os.getenv("S_TOKEN")
BASE_URL = f"https://splus.ir{TOKEN}"

# 🛑 آیدی عددی سروش پلاس خودت (سازنده) را دقیقاً اینجا بگذار
# (می‌توانی آیدی عددی‌ات را با پیام دادن به ربات‌های شناسه مانیتور پیدا کنی)
ADMIN_ID = "آیدی_عددی_شما" 

def send_message(to_id, text):
    """تابع ارسال پیام متنی پایدار"""
    url = f"{BASE_URL}/sendMessage"
    payload = {"to": to_id, "type": "TEXT", "body": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error sending message:", e)

@app.get("/")
def home():
    return {"status": "Pulse Bot is active and running with Admin Panel!"}

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

                # ----------------------------------------------------
                # 🛑 ۱. بخش دستورات داخل گروه (مدیریت گروه پالس)
                # ----------------------------------------------------
                if is_group:
                    if text == "/start" or text == "/setup":
                        send_message(chat_id, "⚡ ربات پالس با موفقیت در این گروه فعال شد و آماده مدیریت است!")
                    
                    elif text.startswith("/ban "):
                        user_to_ban = text.replace("/ban ", "")
                        send_message(chat_id, f"❌ کاربر {user_to_ban} به دستور مدیریت از گروه اخراج شد.")
                
                # ----------------------------------------------------
                # 🛑 ۲. بخش چت خصوصی (پی‌وی ربات)
                # ----------------------------------------------------
                else:
                    # 🔹 الف) اگر فرستنده، خودِ شما (سازنده/ادمین) باشید:
                    if str(chat_id) == str(ADMIN_ID):
                        
                        if text == "/start" or text == "پنل" or text == "/panel":
                            admin_menu = (
                                "👑 **به پنل مدیریت ربات پالس خوش آمدید** 👑\n\n"
                                "شما سازنده این ربات هستید و دسترسی کامل دارید.\n\n"
                                "🛠 **دستورات کلیدی مدیریت:**\n"
                                "▫️ `/stats` -> مشاهده آمار ربات\n"
                                "▫️ `/help` -> راهنمای کامل دستورات گروه\n"
                                "▫️ `/sendtoall [متن]` -> ارسال پیام همگانی به پشتیبانی\n\n"
                                "📮 برای پاسخ به پیام‌های پشتیبانی کاربران، کافیست روی پیام آن‌ها در همین‌جا **ریپلای** کنید."
                            )
                            send_message(chat_id, admin_menu)
                        
                        elif text == "/stats":
                            # در نسخه‌های بعدی این بخش به دیتابیس وصل می‌شود
                            send_message(chat_id, "📊 **آمار فعلی ربات پالس:**\n\nتعداد گروه‌های فعال: در حال محاسبه...\nتعداد کاربران پشتیبانی: فعال")
                        
                        elif text == "/help":
                            help_text = (
                                "📚 **راهنمای دستورات ربات پالس در گروه‌ها:**\n\n"
                                "ابتدا ربات را در گروه ادمین کنید و تیک حذف پیام را بزنید، سپس از دستورات زیر استفاده کنید:\n\n"
                                "🔒 `/lock` -> قفل کردن موقت چت گروه\n"
                                "🔓 `/unlock` -> باز کردن قفل گروه\n"
                                "❌ `/ban [آیدی]` -> اخراج دائم کاربر از گروه\n"
                                "⚠️ `/warn [آیدی]` -> دادن اخطار به کاربر متخلف\n"
                                "⚙️ `/setup` -> بررسی وضعیت اتصال ربات در گروه"
                            )
                            send_message(chat_id, help_text)
                            
                        elif text.startswith("/sendtoall "):
                            broadcast_msg = text.replace("/sendtoall ", "")
                            send_message(chat_id, f"📣 پیام شما برای ارسال همگانی ثبت شد:\n\n{broadcast_msg}")

                    # 🔹 ب) اگر فرستنده، یک کاربر عادی باشد (بخش پشتیبانی پالس):
                    else:
                        if text == "/start":
                            user_welcome = (
                                "سلام! به بخش پشتیبانی پالس خوش آمدید. 🎧\n\n"
                                "پیام، سوال یا مشکل خود را به صورت متنی در ادامه بنویسید و بفرستید.\n"
                                "پیام شما مستقیماً به دست مدیریت می‌رسد و پاسخ آن را همین‌جا دریافت خواهید کرد."
                            )
                            send_message(chat_id, user_welcome)
                        else:
                            # انتقال پیام کاربر عادی به پی‌وی شما (سازنده) همراه با آیدی عددی کاربر برای ریپلای
                            send_message(ADMIN_ID, f"📬 **پیام جدید از طرف کاربر** `[{chat_id}]`:\n\n{text}")
                            send_message(chat_id, "✔️ پیام شما با موفقیت برای مدیریت ارسال شد. لطفاً منتظر پاسخ بمانید.")

    except Exception as e:
        print("Error in webhook system:", e)

    return {"status": "ok"}
    
