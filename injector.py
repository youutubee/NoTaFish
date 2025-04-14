import os

def inject_payload_and_save(template_file, output_dir, user_id):
    if not os.path.exists(template_file):
        return False

    try:
        with open(template_file, "r", encoding="utf-8") as f:
            html = f.read()

        # Inject payload into <form>
        payload = f'<form method="POST" action="/submit/{user_id}">'
        html = html.replace("<form", payload, 1)

        # Save the injected page
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

        return True
    except Exception as e:
        print(f"[ERROR] Payload injection failed: {e}")
        return False
