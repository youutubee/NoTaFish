import os
from bs4 import BeautifulSoup

def inject_payload_and_save(template_file, output_dir, user_id):
    if not os.path.exists(template_file):
        return False

    try:
        with open(template_file, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')

        # Prepare the script tag
        payload_tag = soup.new_tag('script')
        payload_tag.string = f'console.log("Payload injected for user {user_id}");'

        # Try to find the <form> tag
        form_tag = soup.find('form')

        if form_tag:
            form_tag['method'] = 'POST'
            form_tag['action'] = f'/submit/{user_id}'
            form_tag.append(payload_tag)  # Inject inside the form
            print("[INFO] Payload injected into <form>.")
        else:
            # Fallback: inject into <body>
            print(f"[WARNING] No <form> tag found in template: {template_file}")
            body_tag = soup.find('body')
            if body_tag:
                body_tag.append(payload_tag)
                print("[INFO] Payload injected into <body> instead.")
            else:
                print("[ERROR] No <form> or <body> tag found.")
                return False

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the injected page
        output_path = os.path.join(output_dir, "index.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

        print(f"[SUCCESS] File saved to {output_path}")
        return True

    except Exception as e:
        print(f"[ERROR] Payload injection failed: {e}")
        return False
