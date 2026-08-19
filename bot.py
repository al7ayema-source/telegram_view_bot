import os
import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============ توكن البوت ============
TOKEN = os.environ.get("BOT_TOKEN", "ضع_التوكن_هنا")

# ============ سيناريوهات المشاهدة ============
SCENARIOS = [
    {"view": 1.0, "like": True},
    {"view": 1.0, "like": True},
    {"view": 0.5, "like": False},
    {"view": 0.25, "like": False},
    {"view": 0.5, "like": False},
    {"view": 1.0, "like": True},
    {"view": 0.75, "like": False},
] * 3

def setup_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=390,844')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    return driver

def perform_view(driver, url, view_ratio, like=False):
    try:
        driver.get(url)
        time.sleep(3)
        try:
            play_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Play'], .ytp-play-button"))
            )
            play_btn.click()
        except:
            pass
        wait_time = 60 * view_ratio
        time.sleep(min(wait_time, 60))
        if like:
            try:
                like_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='like']")
                like_btn.click()
            except:
                pass
        driver.back()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"خطأ في المشاهدة: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *بوت اختبار المشاهدات*\n\n"
        "أرسل رابط فيديو (يوتيوب، إنستغرام، سناب شات)\n"
        "سأقوم بـ 21 سيناريو مشاهدة مختلفة"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("❌ الرجاء إرسال رابط صحيح")
        return
    
    status_msg = await update.message.reply_text(
        f"🔄 *بدء الاختبار*\n"
        f"🔢 عدد السيناريوهات: 21\n"
        f"⏱️ المدة المتوقعة: 30-45 دقيقة"
    )
    
    def run_test():
        driver = None
        try:
            driver = setup_driver()
            for i, scenario in enumerate(SCENARIOS, 1):
                time.sleep(random.randint(30, 90))
                perform_view(driver, url, scenario["view"], scenario["like"])
                if i % 5 == 0:
                    try:
                        status_msg.edit_text(f"🔄 جاري التنفيذ\n✅ تم: {i}/21")
                    except:
                        pass
            try:
                status_msg.edit_text("✅ *اكتمل الاختبار!*\n\nتم تنفيذ جميع السيناريوهات الـ 21")
            except:
                pass
        except Exception as e:
            try:
                status_msg.edit_text(f"❌ *خطأ*\n\n{str(e)[:200]}")
            except:
                pass
        finally:
            if driver:
                driver.quit()
    
    thread = threading.Thread(target=run_test)
    thread.start()

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("❌ خطأ: لم يتم العثور على توكن البوت")
        print("يرجى إضافة BOT_TOKEN في متغيرات البيئة")
        return
    
    try:
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
        print("✅ البوت يعمل بنجاح!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
