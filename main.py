#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Free Fire Emote Bot - Premium Version
🚀 Optimized for Render.com Hosting
⚡ Dual API System with Auto Failover
"""

import os
import sys
import time
import json
import logging
import requests
import threading
from datetime import datetime
from telebot import TeleBot, types
from telebot.apihelper import ApiException

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8225685692:AAHasKIzHr0f5yL62tCaFz6FrxWUugGKUpw")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6676376793"))

# Dual API Endpoints
API_PRIMARY = "https://ax-ob52-fast-api-2.onrender.com/join"
API_SECONDARY = "https://ax-ob52-fast-api.onrender.com/join"

# Popular Emotes Database
POPULAR_EMOTES = {
    "909000065": "Default Dance",
    "909000075": "Cobra Rising",
    "909000001": "Rage Emote",
    "909000002": "Heart Emote",
    "909000003": "Thumbs Up",
    "909000004": "Victory Dance",
    "909000005": "Laugh",
    "909000006": "Cry",
    "909000007": "Angry",
    "909000008": "Surprised"
}

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Bot
bot = TeleBot(BOT_TOKEN, parse_mode='Markdown', threaded=False)

# Statistics Storage
stats = {
    "total_requests": 0,
    "successful": 0,
    "failed": 0,
    "start_time": datetime.now()
}

# ==================== API HANDLER ====================
class EmoteAPI:
    """Handle dual API system with failover"""
    
    @staticmethod
    def send_emote(team_code, uid, emote_id):
        """
        Try primary API first, failover to secondary if fails
        Returns: dict with success status and details
        """
        endpoints = [
            {"name": "Primary API", "url": f"{API_PRIMARY}?tc={team_code}&uid1={uid}&emote_id={emote_id}"},
            {"name": "Secondary API", "url": f"{API_SECONDARY}?tc={team_code}&uid1={uid}&emote_id={emote_id}"}
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        
        errors = []
        
        for endpoint in endpoints:
            try:
                logger.info(f"Trying {endpoint['name']} for UID {uid}")
                response = requests.get(
                    endpoint['url'], 
                    headers=headers, 
                    timeout=60,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    logger.info(f"Success with {endpoint['name']}")
                    return {
                        'success': True,
                        'api_used': endpoint['name'],
                        'status_code': 200,
                        'response_time': response.elapsed.total_seconds(),
                        'data': response.text[:200] if response.text else "No content"
                    }
                else:
                    errors.append(f"{endpoint['name']}: HTTP {response.status_code}")
                    logger.warning(f"{endpoint['name']} returned {response.status_code}")
                    
            except requests.exceptions.Timeout:
                errors.append(f"{endpoint['name']}: Timeout")
                logger.error(f"{endpoint['name']} timeout")
            except requests.exceptions.ConnectionError:
                errors.append(f"{endpoint['name']}: Connection Error")
                logger.error(f"{endpoint['name']} connection error")
            except Exception as e:
                errors.append(f"{endpoint['name']}: {str(e)}")
                logger.error(f"{endpoint['name']} error: {e}")
        
        # Both failed
        logger.error(f"Both APIs failed: {' | '.join(errors)}")
        return {
            'success': False,
            'error': " | ".join(errors),
            'status_code': 500
        }

# ==================== KEYBOARD MARKUPS ====================
def main_menu():
    """Main menu keyboard"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🎮 Send Emote"),
        types.KeyboardButton("📊 Status"),
        types.KeyboardButton("❓ Help"),
        types.KeyboardButton("🔥 Popular Emotes")
    )
    return markup

def emote_inline_keyboard():
    """Inline keyboard for quick emote selection"""
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for emote_id, name in list(POPULAR_EMOTES.items())[:6]:
        buttons.append(types.InlineKeyboardButton(name, callback_data=f"emote_{emote_id}"))
    markup.add(*buttons)
    return markup

def cancel_keyboard():
    """Cancel operation keyboard"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("❌ Cancel"))
    return markup

# ==================== COMMAND HANDLERS ====================
@bot.message_handler(commands=['start'])
def cmd_start(message):
    """Start command with welcome message"""
    user = message.from_user
    welcome_text = f"""
🎮 *Welcome to Free Fire Emote Bot!* 

Hello {user.first_name}! 👋

I'm your ultimate Free Fire emote sender bot, hosted on Render 24/7!

✨ *Features:*
• Dual API System (Auto Failover)
• Fast Response Time
• Popular Emotes Database
• Real-time Status Check

📱 *Get Started:*
Tap "🎮 Send Emote" below or use:
`/e <team_code> <uid> <emote_id>`

⚡ *Example:*
`/e 8552785 11987556088 909000065`
"""
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['help'])
def cmd_help(message):
    """Detailed help command"""
    help_text = """
📚 *Complete Guide*

*Command List:*

1️⃣ *Send Emote:*
   `/e <team_code> <uid> <emote_id>`
   Example: `/e 8552785 11987556088 909000065`

2️⃣ *Check Status:*
   `/status` - Check API health

3️⃣ *View Statistics:*
   `/stats` - Bot usage stats (Admin only)

4️⃣ *Quick Help:*
   `/help` - Show this message

*Popular Emote IDs:*
"""
    for emote_id, name in POPULAR_EMOTES.items():
        help_text += f"\n• `{emote_id}` - {name}"
    
    help_text += """

💡 *Tips:*
• Make sure all values are numbers
• Team Code is your lobby code
• UID is your Free Fire ID
• API may take 30s on first request (cold start)

❓ Need help? Contact Admin
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['e', 'emote'])
def cmd_emote(message):
    """Main emote sending command"""
    try:
        # Parse arguments
        args = message.text.split()
        
        if len(args) != 4:
            bot.reply_to(message, """
❌ *Invalid Format!*

✅ Correct Format:
`/e <team_code> <uid> <emote_id>`

📋 Example:
`/e 8552785 11987556088 909000065`

💡 Use `/help` for more info
""", parse_mode='Markdown')
            return
        
        team_code, uid, emote_id = args[1], args[2], args[3]
        
        # Validate inputs
        if not (team_code.isdigit() and uid.isdigit() and emote_id.isdigit()):
            bot.reply_to(message, "❌ *Error:* All values must be numbers only!", parse_mode='Markdown')
            return
        
        # Validate lengths (basic check)
        if len(uid) < 8 or len(uid) > 12:
            bot.reply_to(message, "⚠️ *Warning:* UID should be 8-12 digits", parse_mode='Markdown')
        
        # Update stats
        stats['total_requests'] += 1
        
        # Send processing message
        processing_msg = bot.reply_to(message, f"""
⏳ *Processing Request...*

👥 Team Code: `{team_code}`
🆔 UID: `{uid}`
🎭 Emote ID: `{emote_id}`

🔄 Connecting to API...
⏱️ This may take up to 60 seconds
""", parse_mode='Markdown')
        
        # Call API
        result = EmoteAPI.send_emote(team_code, uid, emote_id)
        
        # Delete processing message
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        if result['success']:
            stats['successful'] += 1
            
            # Get emote name if available
            emote_name = POPULAR_EMOTES.get(emote_id, "Custom Emote")
            
            success_text = f"""
✅ *Emote Sent Successfully!*

📊 *Details:*
• 👥 Team Code: `{team_code}`
• 🆔 User ID: `{uid}`
• 🎭 Emote: `{emote_id}` ({emote_name})
• 🌐 API Used: {result['api_used']}
• ⚡ Response Time: {result.get('response_time', 'N/A'):.2f}s
• ⏰ Time: {datetime.now().strftime('%H:%M:%S')}

🎮 Enjoy your emote!
"""
            bot.reply_to(message, success_text)
            logger.info(f"Success: TC={team_code}, UID={uid}, Emote={emote_id}")
            
        else:
            stats['failed'] += 1
            
            error_text = f"""
❌ *Failed to Send Emote*

🔴 *Error Details:*
• Status: Both APIs Failed
• Reason: `{result['error'][:300]}`

💡 *Solutions:*
1. Check your Team Code
2. Verify UID is correct
3. Try again in 30 seconds
4. APIs might be sleeping (Render free tier)

🔄 Use `/status` to check API health
"""
            bot.reply_to(message, error_text)
            logger.error(f"Failed: {result['error']}")
            
    except ApiException as e:
        logger.error(f"Telegram API Error: {e}")
        bot.reply_to(message, "❌ Telegram API Error. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        bot.reply_to(message, f"❌ Unexpected error: `{str(e)[:200]}`")

@bot.message_handler(commands=['status'])
def cmd_status(message):
    """Check API status"""
    msg = bot.reply_to(message, "⏳ *Checking API Status...*\nPlease wait...", parse_mode='Markdown')
    
    status_results = []
    
    # Check Primary API
    try:
        start = time.time()
        r1 = requests.get(API_PRIMARY.replace('/join', ''), timeout=15)
        ping1 = round((time.time() - start) * 1000, 2)
        status_results.append(f"🟢 Primary: {r1.status_code} ({ping1}ms)")
    except:
        status_results.append("🔴 Primary: Offline")
    
    # Check Secondary API
    try:
        start = time.time()
        r2 = requests.get(API_SECONDARY.replace('/join', ''), timeout=15)
        ping2 = round((time.time() - start) * 1000, 2)
        status_results.append(f"🟢 Secondary: {r2.status_code} ({ping2}ms)")
    except:
        status_results.append("🔴 Secondary: Offline")
    
    bot.delete_message(message.chat.id, msg.message_id)
    
    uptime = datetime.now() - stats['start_time']
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    status_text = f"""
🚦 *System Status Report*

{'\n'.join(status_results)}

📊 *Bot Statistics:*
• 📈 Total Requests: {stats['total_requests']}
• ✅ Successful: {stats['successful']}
• ❌ Failed: {stats['failed']}
• ⏱️ Uptime: {hours}h {minutes}m {seconds}s
• 🕐 Current Time: {datetime.now().strftime('%H:%M:%S')}

💡 *Note:* APIs may sleep on Render free tier
"""
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    """Admin statistics command"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 *Access Denied*\nThis command is for admin only!", parse_mode='Markdown')
        return
    
    uptime = datetime.now() - stats['start_time']
    
    stats_text = f"""
🔐 *Admin Statistics*

📊 *Usage Stats:*
• Total Requests: `{stats['total_requests']}`
• Successful: `{stats['successful']}`
• Failed: `{stats['failed']}`
• Success Rate: `{(stats['successful']/stats['total_requests']*100) if stats['total_requests'] > 0 else 0:.1f}%`

⏱️ *System Info:*
• Uptime: `{str(uptime).split('.')[0]}`
• Bot ID: `{bot.get_me().id}`
• Admin ID: `{ADMIN_ID}`

🌐 *API Endpoints:*
• Primary: `{API_PRIMARY}`
• Secondary: `{API_SECONDARY}`
"""
    bot.reply_to(message, stats_text)

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    """Admin broadcast command"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        text = message.text.replace('/broadcast ', '', 1)
        if not text:
            bot.reply_to(message, "❌ Usage: `/broadcast <message>`")
            return
        
        # Here you would implement user database broadcast
        bot.reply_to(message, f"📢 Broadcast sent:\n{text}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ==================== BUTTON HANDLERS ====================
@bot.message_handler(func=lambda m: m.text == "🎮 Send Emote")
def btn_send_emote(message):
    bot.reply_to(message, """
🎮 *Send Emote*

Use command:
`/e <team_code> <uid> <emote_id>`

Or select popular emote below:
""", reply_markup=emote_inline_keyboard())

@bot.message_handler(func=lambda m: m.text == "📊 Status")
def btn_status(message):
    cmd_status(message)

@bot.message_handler(func=lambda m: m.text == "❓ Help")
def btn_help(message):
    cmd_help(message)

@bot.message_handler(func=lambda m: m.text == "🔥 Popular Emotes")
def btn_popular(message):
    text = "🔥 *Popular Emotes*\n\nClick to copy ID:\n\n"
    for emote_id, name in POPULAR_EMOTES.items():
        text += f"`{emote_id}` - {name}\n"
    text += "\n💡 Use: `/e <tc> <uid> <emote_id>`"
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "❌ Cancel")
def btn_cancel(message):
    bot.reply_to(message, "✅ Cancelled.", reply_markup=main_menu())

# ==================== CALLBACK HANDLERS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('emote_'))
def callback_emote(call):
    """Handle emote selection from inline keyboard"""
    emote_id = call.data.replace('emote_', '')
    emote_name = POPULAR_EMOTES.get(emote_id, "Unknown")
    
    bot.answer_callback_query(call.id, f"Selected: {emote_name}")
    bot.send_message(
        call.message.chat.id,
        f"✅ Selected: *{emote_name}*\n🎭 ID: `{emote_id}`\n\nNow use:\n`/e <team_code> <uid> {emote_id}`",
        parse_mode='Markdown'
    )

# ==================== GROUP HANDLERS ====================
@bot.message_handler(content_types=['new_chat_members'])
def on_user_join(message):
    """Welcome message when bot added to group"""
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            welcome = """
🎉 *Thanks for adding me!*

I'm Free Fire Emote Bot!

📋 *How to use:*
`/e <team_code> <uid> <emote_id>`

⚡ Example:
`/e 8552785 11987556088 909000065`

❓ More help: `/help`

⚠️ *Make me admin for best performance!*
"""
            bot.send_message(message.chat.id, welcome, parse_mode='Markdown')
            logger.info(f"Added to group: {message.chat.title}")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    """Handle unknown messages"""
    if message.chat.type == 'private':
        bot.reply_to(message, """
❓ I didn't understand that.

Use buttons below or type `/help` for assistance.
""", reply_markup=main_menu())

# ==================== ERROR HANDLER ====================
@bot.error_handler
def error_handler(exception):
    """Global error handler"""
    logger.error(f"Bot error: {exception}")
    return True

# ==================== MAIN ====================
def main():
    """Main function"""
    print("=" * 60)
    print("🎮 Free Fire Emote Bot - Premium")
    print("🚀 Render.com Optimized")
    print("⚡ Dual API System")
    print("=" * 60)
    
    try:
        me = bot.get_me()
        print(f"✅ Bot: @{me.username}")
        print(f"🆔 ID: {me.id}")
        print(f"👤 Name: {me.first_name}")
        print(f"👑 Admin: {ADMIN_ID}")
        print("=" * 60)
        print("🤖 Bot is running...")
        print("💡 Press Ctrl+C to stop")
        print("=" * 60)
        
        logger.info("Bot started successfully")
        
        # Start polling
        bot.polling(
            none_stop=True,
            interval=0,
            timeout=30,
            long_polling_timeout=60
        )
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        time.sleep(10)
        main()

if __name__ == "__main__":
    main()
