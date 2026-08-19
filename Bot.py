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
TOKEN = os.environ.get("BOT_TOKEN", "ضع_التوكن_هنا_احتياطياً")

# ============ سيناريوهات المشاهدة ============
SCENARIOS = [
    {"view": 1.0, "like": True, "action": "مشاهدة كاملة + لايك"},
    {"view": 1.0, "like": True, "action": "مشاهدة كاملة + لايك (تكرار)"},
    {"view": 0.5, "like": False, "action": "مشاهدة 50%"},
    {"view": 0.25, "like": False, "action": "مشاهدة 25%"},
    {"view": 0.5, "like": False, "action": "مشاهدة 50% بدون لايك"},
    {"view": 1.0, "like": True, "action": "مشاهدة كاملة + لايك"},
    {"view": 0.75, "like": False, "action": "مشاهدة 75%"},
]

def generate_scenarios():
    all_scenarios = []
    for cycle in range(3):
        for scenario in SCENARIOS:
            scenario_copy = scenario.copy()
            scenario_copy['cycle'] = cycle + 1
            scenario_copy['delay'] = random.randint(30, 90)
            all_scenarios.append(scenario_copy)
        if cycle < 2:
            all_scenarios.append({'delay_between': random.randint(300, 600)})
    return all_scenarios

def setup_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=390,844')
    options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
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
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *بوت اختبار المشاهدات*\n\n"
        "أرسل رابط فيديو (يوتيوب، إنستغرام، سناب شات)\n"
        "سأقوم بـ 21 سيناريو مشاهدة مختلفة"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user = update.effective_user.first_name
    
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("❌ الرجاء إرسال رابط صحيح")
        return
    
    status_msg = await update.message.reply_text(
        f"🔄 *بدء الاختبار*\n"
        f"📱 المستخدم: {user}\n"
        f"🔢 عدد السيناريوهات: 21\n"
        f"⏱️ المدة المتوقعة: 30-45 دقيقة"
    )
    
    def run_test():
        scenarios = generate_scenarios()
        driver = None
        try:
            driver = setup_driver()
            for i, scenario in enumerate(scenarios, 1):
                if 'delay_between' in scenario:
                    time.sleep(scenario['delay_between'])
                    continue
                time.sleep(scenario['delay'])
                perform_view(driver, url, scenario['view'], scenario['like'])
                if i % 5 == 0 or i == len(scenarios):
                    threading.Thread(target=lambda: update_status(status_msg, i, len(scenarios))).start()
            threading.Thread(target=lambda: finalize_test(status_msg)).start()
        except Exception as e:
            threading.Thread(target=lambda: error_test(status_msg, str(e))).start()
        finally:
            if driver:
                driver.quit()
    
    thread = threading.Thread(target=run_test)
    thread.start()

def update_status(status_msg, current, total):
    try:
        status_msg.edit_text(
            f"🔄 *جاري التنفيذ*\n"
            f"✅ تم: {current}/{total}"
        )
    except:
        pass

def finalize_test(status_msg):
    try:
        status_msg.edit_text("✅ *اكتمل الاختبار!*\n\nتم تنفيذ جميع السيناريوهات الـ 21")
    except:
        pass

def error_test(status_msg, error):
    try:
        status_msg.edit_text(f"❌ *خطأ*\n\n{error[:200]}")
    except:
        pass

def main():
    if not TOKEN or TOKEN == "ضع_التوكن_هنا_احتياطياً":
        print("❌ خطأ: لم يتم العثور على توكن البوت")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    print("🤖 البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()  
