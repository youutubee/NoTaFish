import os
from bs4 import BeautifulSoup

def inject_payload_and_save(template_file, output_dir, user_id):
    if not os.path.exists(template_file):
        return False

    try:
        with open(template_file, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        form_tag = soup.find('form')

        if form_tag:
            form_tag['method'] = 'POST'
            form_tag['action'] = f'/submit/{user_id}'
        else:
            print(f"[ERROR] No <form> tag found in template: {template_file}")
            return False

        # Save the injected page
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(str(soup))

        return True
    except Exception as e:
        print(f"[ERROR] Payload injection failed: {e}")
        return False
