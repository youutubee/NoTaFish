<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>PhishBot - System Architecture</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 2rem;
      background-color: #f9f9f9;
      line-height: 1.6;
    }
    h2, h3, h4 {
      color: #2c3e50;
    }
    pre {
      background: #eee;
      padding: 1rem;
      border-radius: 6px;
      overflow-x: auto;
    }
    code {
      background: #f4f4f4;
      padding: 2px 6px;
      border-radius: 4px;
    }
    ul {
      padding-left: 1.5rem;
    }
  </style>
</head>
<body>

  <h2>2. System Architecture</h2>

  <h3>2.1 Components Overview</h3>
  <p>The PhishBot application consists of two main components:</p>
  <ul>
    <li><strong>Telegram Bot:</strong> Handles user interaction, command processing, and phishing page generation</li>
    <li><strong>Flask Web Server:</strong> Serves phishing pages, captures credentials, and forwards them to the Telegram bot</li>
  </ul>

  <p>These components work together to create a complete phishing simulation system:</p>
  <pre>[User] &lt;---&gt; [Telegram Bot] &lt;---&gt; [Flask Web Server] &lt;---&gt; [Victim]</pre>

  <h3>2.2 Directory Structure</h3>
  <pre>
/
├── app.py                       # Main application code
├── captured_credentials.json    # Storage for captured credentials
├── Templates/                   # Template directory
│   ├── Instagram/
│   │   └── index.html
│   ├── Facebook/
│   │   └── index.html
│   └── [Other templates]/
└── phished_pages/
    └── [user_id]/
        ├── index.html
        ├── template_info.txt
        └── [assets]/
  </pre>

  <h2>3. Hosting and Deployment Architecture</h2>
  <p>The application is designed to be hosted on Render.com, which provides:</p>
  <ul>
    <li><strong>Continuous Deployment:</strong> Automatically deploys from a GitHub repository</li>
    <li><strong>Web Service:</strong> Hosts both the Flask web server and Telegram bot in one application</li>
    <li><strong>Environment Variables:</strong> Uses <code>PORT</code> for Render compatibility</li>
  </ul>

  <h3>3.1 Render.com Configuration</h3>
  <ul>
    <li><strong>Service Type:</strong> Web Service</li>
    <li><strong>Runtime:</strong> Python</li>
    <li><strong>Build Command:</strong> <code>pip install -r requirements.txt</code></li>
    <li><strong>Start Command:</strong> <code>python app.py</code></li>
    <li><strong>Environment Variables:</strong></li>
    <ul>
      <li><code>PORT</code>: Set by Render automatically</li>
      <li><em>No need for API_TOKEN as it's hardcoded</em></li>
    </ul>
  </ul>

  <h3>3.2 Network Architecture</h3>
  <pre>
Render.com
└── Web Service (app.py)
    ├── Flask Server (Port from env)
    │   ├── /phish/&lt;user_id&gt; routes
    │   └── /submit/&lt;user_id&gt; routes
    └── Telegram Bot (Background Thread)
        └── Connected to Telegram API
  </pre>

  <h2>4. Form Modification Process</h2>

  <h3>4.1 Overview</h3>
  <ul>
    <li>User selects a template through Telegram</li>
    <li>Template is copied to a user-specific directory</li>
    <li>HTML form is modified to send data to the Flask server</li>
    <li>User gets a unique phishing URL to share with victims</li>
  </ul>

  <h3>4.2 HTML Modification Details</h3>
  <p>The <code>modify_html_form()</code> function does the following:</p>
  <ul>
    <li>Reads the HTML file</li>
    <li>Uses regex to find all form elements</li>
    <li>Preserves form method (GET/POST)</li>
    <li>Updates form action to <code>/submit/&lt;user_id&gt;</code></li>
    <li>Adds a hidden tracking field</li>
    <li>Handles various HTML form structures</li>
    <li>Writes back the modified HTML</li>
  </ul>

  <p>Regex handles various form formats:</p>
  <pre>
&lt;form action="..." method="..."&gt;
&lt;form method="..." action="..."&gt;
&lt;form method="..."&gt;
&lt;form action="..."&gt;
&lt;form&gt;
  </pre>

  <h2>5. Credential Capture Process</h2>
  <p>When a victim submits credentials:</p>
  <ul>
    <li>Data sent to <code>/submit/&lt;user_id&gt;</code></li>
    <li>Flask extracts form data from POST/GET</li>
    <li>Metadata (timestamp, IP, user agent) is added</li>
    <li>Credentials forwarded via Telegram</li>
    <li>Stored in <code>captured_credentials.json</code></li>
    <li>Victim redirected to real website</li>
  </ul>

  <h3>5.1 Data Processing</h3>
  <pre><code>if request.method == 'POST':
    creds = request.form.to_dict()
else:  # GET method
    creds = request.args.to_dict()</code></pre>
  <p>This ensures compatibility with both GET and POST forms.</p>

  <h2>6. Session Management</h2>
  <ul>
    <li><strong>User directories:</strong> Unique per Telegram user</li>
    <li><strong>Template tracking:</strong> Stored in <code>template_info.txt</code></li>
    <li><strong>Credential storage:</strong> Stored in a JSON file by user ID</li>
  </ul>

  <h2>7. Security Considerations</h2>
  <ul>
    <li>Isolation of phishing pages per user</li>
    <li>Robust error handling</li>
    <li>Comprehensive logging</li>
    <li>Thread safety via background thread for bot</li>
  </ul>

  <h2>8. Testing Recommendations</h2>
  <ul>
    <li>Test various social login forms</li>
    <li>Ensure all fields are captured</li>
    <li>Check logs for parsing issues</li>
    <li>Test with both GET and POST methods</li>
  </ul>

  <h2>Conclusion</h2>
  <p>The enhanced PhishBot now properly captures credentials, has improved HTML parsing, and is ready for scalable deployment on Render.com. The critical issue with form data capturing is fixed using smarter regex parsing and logging.</p>

  <h2>Deployment Instructions</h2>

  <h3>1. Fork this repository to your GitHub account.</h3>

  <h3>2. Create a new Web Service on Render.com:</h3>
  <ul>
    <li>Connect your GitHub repository</li>
    <li>Select the Python runtime</li>
    <li>Set the following configuration:</li>
    <ul>
      <li>Build Command: <code>pip install -r requirements.txt</code></li>
      <li>Start Command: <code>gunicorn app:app</code></li>
    </ul>
    <li>Add environment variables:</li>
    <ul>
      <li><code>PORT</code>: Leave empty (Render will set this)</li>
      <li><code>PYTHON_VERSION</code>: <code>3.9.12</code></li>
    </ul>
  </ul>

  <h3>3. The deployment will automatically start. Once complete, your bot will be accessible at:</h3>
  <p><code>https://your-app-name.onrender.com</code></p>

  <h3>4. Test the deployment by sending <code>/start</code> to your Telegram bot.</h3>

  <h2>Directory Structure</h2>
  <pre>
/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── Procfile                 # Render deployment configuration
├── Templates/               # Phishing templates
│   ├── Facebook/
│   ├── Instagram/
│   └── Sample/
└── phished_pages/          # Generated pages (created at runtime)
  </pre>

  <h2>Available Commands</h2>
  <ul>
    <li><code>/start</code> - Start the bot</li>
    <li><code>/help</code> - Show help message</li>
    <li><code>/fish</code> - Start phishing setup</li>
    <li><code>/templates</code> - List available templates</li>
    <li><code>/info</code> - About the bot</li>
    <li><code>/history</code> - View captured credentials</li>
  </ul>

  <h2>Security Notes</h2>
  <ul>
    <li>This is for educational purposes only</li>
    <li>Do not use for malicious purposes</li>
    <li>All data is stored temporarily</li>
    <li>No real credentials are harvested</li>
  </ul>

  <h2>Troubleshooting</h2>
  <ul>
    <li>If pages show "not found":
      <ul>
        <li>Check if Templates directory exists</li>
        <li>Verify template files are present</li>
        <li>Check logs for path errors</li>
      </ul>
    </li>
    <li>If bot doesn't respond:
      <ul>
        <li>Verify API_TOKEN is correct</li>
        <li>Check if bot is running</li>
        <li>View logs for errors</li>
      </ul>
    </li>
  </ul>

  <h2>Maintenance</h2>
  <ul>
    <li>Keep dependencies updated</li>
    <li>Monitor disk usage</li>
    <li>Check logs regularly</li>
    <li>Backup templates if needed</li>
  </ul>

</body>
</html>
