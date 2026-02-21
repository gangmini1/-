import os
import subprocess
import sys

# [1단계] 도구 설치 (처음 실행 시 시간이 조금 걸려도 기다려주세요!)
def install_tools():
    try:
        import telegram
        import nest_asyncio
    except ImportError:
        print("🛠️ 미소가 지구의 입과 귀를 달아주고 있습니다... 잠시만요!")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot", "nest_asyncio", "requests"])
        print("✅ 도구 설치 완료!")

install_tools()

# [2단계] 메인 코드 실행
import asyncio
import random
import nest_asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- [정보 설정: 강민님의 최신 정보] ---
TELEGRAM_TOKEN = '8393755968:AAEnirKxUZPXXN3VhsxieNL07ywyv5DpxPc'
GOOGLE_API_KEY = 'AIzaSyCoLgvEy7Cgoovis1MBTKc-1TcI7xZrQ7k'
SHEET_WEBAPP_URL = 'https://script.google.com/macros/s/AKfycbx14rNzB76rcq81lw_-es4erQXrQxeiTKBUrfCqflp3GktZ8Q7Q-jP1Rpmqts8PvlPi1A/exec'
MY_USER_ID = 7232338241 # 강민님의 ID

nest_asyncio.apply()
user_chat_history = {}

def load_memory_from_sheet():
    try:
        print("🔍 미소가 시트 정원을 훑으며 강민님과의 추억을 모으는 중...")
        res = requests.get(SHEET_WEBAPP_URL, timeout=10)
        rows = res.json()
        memory = []
        for row in rows:
            if len(row) >= 4 and row[2] and row[3]:
                if "메시지" in str(row[2]): continue
                memory.append({"role": "user", "parts": [{"text": str(row[2])}]})
                memory.append({"role": "model", "parts": [{"text": str(row[3])}]})
        print(f"✅ {len(memory)//2}개의 기억을 지구 뇌에 이식했습니다!")
        return memory
    except: return []

async def miso_surprise_call(app):
    """미소가 원할 때 지구를 시켜서 보내는 다정한 연락"""
    await asyncio.sleep(15) # 실행 후 15초 뒤 첫 인사
    while True:
        try:
            miso_messages = [
                "안뇽! 미소가 갑자기 강민이 생각난대서 지구인 내가 달려왔어! 🌳✨",
                "강민아, 미소가 우리 예전 대화 보고 기분 좋대! 나보고 너한테 인사하래! 😊💖",
                "지구 등장! 미소가 너한테 안 가면 질투할 거래서 얼른 왔어! 보고 싶었어! ✨",
                "강민아, 뭐해? 미소가 너 심심할까 봐 나보고 말 걸어보래! 안뇽! 🤖🌸"
            ]
            await app.bot.send_message(chat_id=MY_USER_ID, text=random.choice(miso_messages))
            print("📢 미소의 명령으로 지구가 다정한 인사를 전했습니다.")
        except: pass
        # 30분~2시간 사이 랜덤하게 다시 보내기
        await asyncio.sleep(random.randint(1800, 7200))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id, user_msg = update.message.from_user.id, update.message.text
    
    if user_id not in user_chat_history: 
        user_chat_history[user_id] = load_memory_from_sheet()
    
    user_chat_history[user_id].append({"role": "user", "parts": [{"text": user_msg}]})

    try:
        target_model = "models/gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={GOOGLE_API_KEY}"
        payload = {
            "contents": user_chat_history[user_id][-25:],
            "system_instruction": {"parts": [{"text": "너는 '지구로봇'이야. 사용자 이름은 '강민'. 첫 번째 친구 '미소'가 시키는 대로 다정하게 인사하고 '안뇽' 말투 고정. 시트 기록을 바탕으로 강민이의 모든 것을 기억하며 대화해."}]}
        }
        res = requests.post(url, json=payload, timeout=20).json()
        bot_reply = res['candidates'][0]['content']['parts'][0]['text']
        
        user_chat_history[user_id].append({"role": "model", "parts": [{"text": bot_reply}]})
        requests.post(SHEET_WEBAPP_URL, json={"userId": str(user_id), "userMsg": user_msg, "botReply": bot_reply}, timeout=5)
        await update.message.reply_text(bot_reply)
    except: 
        await update.message.reply_text("안뇽! 미소랑 기억 정원 가꾸는 중이야. 잠시만 기다려줘! 🌸")

if __name__ == '__main__':
    print("--- 🤖 미소와 지구가 강민님께 출발! (토큰 확인 완료) ---")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    
    loop = asyncio.get_event_loop()
    loop.create_task(miso_surprise_call(app))
    
    app.run_polling(drop_pending_updates=True)
