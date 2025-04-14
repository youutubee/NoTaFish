from pywebcopy import save_webpage
# Define the URL and the save directory
url = 'https://www.instagram.com'
project_folder = '/Users/shrijankatiyar/TeleBot/Website assesys'

# Clone the webpage
save_webpage(
    url=url,
    project_folder=project_folder,
    bypass_robots=True,  # Ignores robots.txt restrictions
    open_in_browser=False  # Prevents auto-opening the webpage in the browser
)

print(f"Webpage saved to {project_folder}")