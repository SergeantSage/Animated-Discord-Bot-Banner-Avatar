import requests
import base64
import os
import time
from dotenv import load_dotenv
from flask import Flask
from colorama import Fore, Style, init
import logging

init()

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('TOKEN')

if not DISCORD_BOT_TOKEN:
    print(f"{Fore.RED}Error: TOKEN environment variable not set.{Style.RESET_ALL}")
    exit()

PROFILE_IMAGE_URL = "https://media.discordapp.net/attachments/1208810080426795061/1271602484061671424/Gido-PFP-Carl.gif?ex=66b9e9d9&is=66b89859&hm=435b9550427e5f05bbff780e509e83170057b9f576f2380b672826c6b346c801&="
BANNER_IMAGE_URL = "https://media.discordapp.net/attachments/1208810080426795061/1271602484519112724/Gido-Banner-Carl.gif?ex=66b9e9d9&is=66b89859&hm=36cef24fa243affd09339b811aff865f0169dd29cd64b453724963d13e4941e8&="

payload = {}

FLAG_FILE = 'profile_update_flag.txt'

if os.path.exists(FLAG_FILE):
    print(f"{Fore.YELLOW}The profile has already been updated. Exiting.{Style.RESET_ALL}")
    exit()

banner_update_status = "Not Updated"
avatar_update_status = "Not Updated"

if PROFILE_IMAGE_URL:
    profile_image_response = requests.get(PROFILE_IMAGE_URL)
    if profile_image_response.status_code == 200:
        profile_image_base64 = base64.b64encode(profile_image_response.content).decode('utf-8')
        payload["avatar"] = f"data:image/gif;base64,{profile_image_base64}"
        avatar_update_status = "Success"
    else:
        print(f"{Fore.RED}Failed to download profile picture.{Style.RESET_ALL}")

if BANNER_IMAGE_URL:
    banner_image_response = requests.get(BANNER_IMAGE_URL)
    if banner_image_response.status_code == 200:
        banner_image_base64 = base64.b64encode(banner_image_response.content).decode('utf-8')
        payload["banner"] = f"data:image/gif;base64,{banner_image_base64}"
        banner_update_status = "Success"
    else:
        print(f"{Fore.RED}Failed to download banner.{Style.RESET_ALL}")

if payload:
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }

    while True:
        response = requests.patch('https://discord.com/api/v10/users/@me', headers=headers, json=payload)

        if response.status_code == 200:
            break
        elif response.status_code == 429:
            retry_after = response.json().get('retry_after', 60)
            print(f"{Fore.YELLOW}Rate limit exceeded. Retrying after {retry_after} seconds...{Style.RESET_ALL}")
            time.sleep(retry_after)
        elif response.status_code == 401:
            print(f"{Fore.RED}Invalid token. Please check your token and try again.{Style.RESET_ALL}")
            break
        elif response.status_code == 50035:
            print(f"{Fore.RED}Avatar rate limit exceeded. Try again later.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Failed to update profile and/or banner: {response.text}{Style.RESET_ALL}")
            break
else:
    print(f"{Fore.YELLOW}No updates to make. Both profile and banner URLs were blank.{Style.RESET_ALL}")

with open(FLAG_FILE, 'w') as f:
    f.write('Profile update script has run.')

app = Flask(__name__)

@app.route('/')
def index():
    return "Profile update script has run."

if __name__ == "__main__":
    # Suppress Flask's logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    port = int(os.environ.get("PORT", 10000))

    print(f'\n{Fore.GREEN}🎨 Banner Update: {banner_update_status}{Style.RESET_ALL}')
    print(f'{Fore.GREEN}🎨 Avatar Update: {avatar_update_status}{Style.RESET_ALL}')
    print(f'{Fore.GREEN}🚀 Running on Port: {port}{Style.RESET_ALL}')
    print(f'{Fore.GREEN}⚙️ Powered by Carl, GlaceYT{Style.RESET_ALL}')

    app.run(host='0.0.0.0', port=port, debug=False)
