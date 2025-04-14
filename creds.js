import os

def inject_payload(template_name, payload):
    # Adjusted path to target the correct subfolder structure
    template_path = f"Templates/{template_name}/index.html"
    
    try:
        # Read the template file
        with open(template_path, 'r') as file:
            content = file.read()

        # Inject the payload (insert in a <script> tag or specific placeholder in the HTML)
        payload_code = f"<script>{payload}</script>"
        content = content.replace("<!-- Placeholder for payload injection -->", payload_code)

        # Save the modified template to a new file in the 'clones' folder
        output_path = f"clones/{template_name}_cloned.html"
        with open(output_path, 'w') as file:
            file.write(content)
        
        return output_path
    
    except FileNotFoundError:
        return None
