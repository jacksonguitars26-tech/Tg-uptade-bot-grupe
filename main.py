#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Free Fire Emote Bot - Render Optimized
"""

import os
import time
import requests
from telebot import TeleBot, types

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225685692:AAHasKIzHr0f5yL62tCaFz6FrxWUugGKUpw")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6676376793"))

API_1 = "https://ax-ob52-fast-api-2.onrender.com/join"
API_2 = "https://ax-ob52-fast-api.onrender.com/join"

bot = TeleBot(BOT_TOKEN, parse_mode='Markdown')

# ==================== API FUNCTION ====================
def send_emote_api(team_code, uid, emote_id):
    """Try both APIs"""
    apis = [
        (API_1, "Primary"),
        (API_2, "Secondary")
    ]
    
    for api_url, name in apis:
        try:
            url = f"{api_url}?tc={team_code}&uid1={uid}&emote_id={emote_id}"
            r = requests.get(url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                return {'success': True, 'api': name}
        except:
            continue
    
    return {'success': False}

# ==================== COMMANDS ====================

@bot.message_handler(commands=['start'])
def start(message):
    text = """
🎮 *Free Fire Emote Bot*

✅ Bot is Online!

📋 *Commands:*
• `/e <tc> <uid> <emote>` - Send emote
• `/status` - Check API status

⚡ *Example:*
`/e 8552785 11987556088 909000065`
"""
    bot.reply_to(message, text)

@bot.message_handler(commands=['e'])
def emote(message):
    try:
        args = message.text.split()
        
        if len(args) != 4:
            bot.reply_to(message, "❌ Format: `/e <team_code> <uid> <emote_id>`")
            return
        
        tc, uid, emote_id = args[1], args[2], args[3]
        
        if not (tc.isdigit() and uid.isdigit() and emote_id.isdigit()):
            bot.reply_to(message, "❌ All values must be numbers!")
            return
        
        # Processing
        msg = bot.reply_to(message, f"⏳ Sending emote to `{uid}`...")
        
        # Call API
        result = send_emote_api(tc, uid, emote_id)
        
        # Delete processing message
        bot.delete_message(message.chat.id, msg.message_id)
        
        if result['success']:
            bot.reply_to(message, f"""
✅ *Success!*

👤 UID: `{uid}`
🎭 Emote: `{emote_id}`
🌐 API: {result['api']}
""")
        else:
            bot.reply_to(message, """
❌ *Failed!*

Both APIs are down or sleeping.
Try again in 30-60 seconds.
""")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['status'])
def status(message):
    try:
        r1 = requests.get(API_1.replace('/join',''), timeout=10)
        r2 = requests.get(API_2.replace('/join',''), timeout=10)
        
        text = f"""
🚦 *API Status*

🟢 Primary: {r1.status_code}
🟢 Secondary: {r2.status_code}
"""
    except:
        text = """
🚦 *API Status*

🔴 Primary: Offline
🔴 Secondary: Offline

💡 APIs may be sleeping. Try again later.
"""
    bot.reply_to(message, text)

# ==================== MAIN ====================
print("=" * 50)
print("🎮 Free Fire Emote Bot")
print("🚀 Starting on Render...")
print("=" * 50)

try:
    me = bot.get_me()
    print(f"✅ Bot: @{me.username}")
    print("🤖 Running...")
    
    # Start bot
    bot.polling(none_stop=True, interval=0, timeout=30)
    
except Exception as e:
    print(f"❌ Error: {e}")
    time.sleep(10)
    # Retry
    bot.polling(none_stop=True, interval=0, timeout=30)
