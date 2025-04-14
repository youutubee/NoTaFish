from flask import Flask, render_template_string
import os

app = Flask(__name__)

def inject_payload(html_content, payload):
    """Inject a payload into the HTML content."""
    script_tag = f"<script>{payload}</script>"
    return html_content.replace('</body>', f'{script_tag}</body>')

@app.route('/')
def serve_cloned_page():
    # Path to the template
    template_path = "Templates/Instagram/index.html"

    # Check if the template exists
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Define a test payload to inject (you can customize this)
        payload = "alert('This is a test payload!');"

        # Inject the payload into the HTML content
        modified_html = inject_payload(html_content, payload)

        # Return the modified HTML using Flask's render_template_string
        return render_template_string(modified_html)
    else:
        return "❌ Template file not found!"


if __name__ == '__main__':
    # Start Flask server locally
    app.run(port=5000)  # Start the Flask app
