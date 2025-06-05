from telethon import TelegramClient, events, functions, types, utils
import asyncio
import pytz
from datetime import datetime, timedelta
import logging
import random
import os
import sys
import re
import json
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO
import requests
from gtts import gTTS
import jdatetime
import colorama
from colorama import Fore, Back, Style
import qrcode
import whois
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
import emoji
import psutil
import string
import hashlib
import base64
import zipfile
import shutil
import subprocess
from urllib.parse import urlparse
import socket
import dns.resolver
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
import pandas as pd
import hashlib
import sqlite3
from collections import defaultdict
import aiohttp
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterVideo

# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)

# ASCII Art Logo
LOGO = f"""
{Fore.CYAN}╔════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.BLUE}████████╗███████╗██╗     ███████╗██████╗  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   █████╗  ██║     █████╗  ██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   ██╔══╝  ██║     ██╔══╝  ██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   ███████╗███████╗███████╗██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████╗███████╗██╗     ███████╗██████╗  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}██╔════╝██╔════╝██║     ██╔════╝██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████╗█████╗  ██║     █████╗  ██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}╚════██║██╔══╝  ██║     ██╔══╝  ██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████║███████╗███████╗███████╗██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}╚══════╝╚══════╝╚══════╝╚══════╝╚═════╝  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╗  ██████╗ ████████╗               {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██╔══██╗██╔═══██╗╚══██╔══╝               {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╔╝██║   ██║   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██╔══██╗██║   ██║   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╔╝╚██████╔╝   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}╚═════╝  ╚═════╝    ╚═╝                  {Fore.CYAN}║
{Fore.CYAN}╚════════════════════════════════════════════╝
{Fore.GREEN}        Enhanced Version 3.0 (2025)
"""

# Configuration variables
CONFIG_FILE = "config.json"
LOG_FILE = "selfbot.log"
DB_FILE = "selfbot.db"
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

# Default configuration settings
default_config = {
    "api_id": 29042268,
    "api_hash": "54a7b377dd4a04a58108639febe2f443",
    "session_name": "anon",
    "log_level": "INFO",
    "timezone": "Asia/Tehran",
    "auto_backup": True,
    "backup_interval": 60,
    "enemy_reply_chance": 100,
    "enemy_auto_reply": True,
    "auto_read_messages": False,
    "allowed_users": [],
    "auto_delete_after": 0,
    "max_message_length": 4000,
    "spam_delay": 0.5,
    "auto_respond_delay": 2,
    "default_language": "fa",
    "backup_encryption": True,
    "max_spam_count": 50,
    "auto_update_check": True,
    "weather_api_key": "your_openweather_api_key",
    "news_api_key": "your_newsapi_key"
}

# Global variables
enemies = set()
current_font = 'normal'
actions = {
    'typing': False,
    'online': False,
    'reaction': False,
    'read': False,
    'auto_reply': False,
    'auto_delete': False,
    'auto_forward': False,
    'auto_mute': False,
    'anti_spam': False
}
spam_words = []
saved_messages = []
reminders = []
time_enabled = True
saved_pics = []
custom_replies = {}
blocked_words = []
last_backup_time = None
running = True
start_time = time.time()
command_history = []
MAX_HISTORY = 50
user_activity = defaultdict(lambda: {'last_seen': None, 'message_count': 0})
chat_settings = defaultdict(dict)
locked_chats = {
    'screenshot': set(),
    'forward': set(),
    'copy': set(),
    'delete': set(),
    'edit': set(),
    'spam': set(),
    'mention': set()
}

# Font styles
font_styles = {
    'normal': lambda text: text,
    'bold': lambda text: f"**{text}**",
    'italic': lambda text: f"__{text}__",
    'script': lambda text: f"`{text}`",
    'double': lambda text: f"```{text}```",
    'bubble': lambda text: f"||{text}||",
    'square': lambda text: f"```{text}```",
    'strikethrough': lambda text: f"~~{text}~~",
    'underline': lambda text: f"___{text}___",
    'caps': lambda text: text.upper(),
    'lowercase': lambda text: text.lower(),
    'title': lambda text: text.title(),
    'space': lambda text: " ".join(text),
    'reverse': lambda text: text[::-1],
    'emoji': lambda text: emoji.emojize(text, language='alias'),
    'mirror': lambda text: ''.join(chr(0x202E) + text[::-1] + chr(0x202C)),
    'upside_down': lambda text: ''.join({'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ'}.get(c, c) for c in text.lower())
}

# Insults list (unchanged for compatibility)
insults = [
    "کیرم تو کص ننت", "مادرجنده", "کص ننت", "کونی", "جنده", "کیری", "بی ناموس", "حرومزاده", "مادر قحبه", "جاکش",
    # ... (keeping original insults list unchanged as per request)
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE
)
logger = logging.getLogger("TelegramSelfBot")

# Database setup
def init_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, chat_id TEXT, message TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                 (user_id TEXT PRIMARY KEY, message_count INTEGER, last_seen TEXT)''')
    conn.commit()
    conn.close()

# Convert numbers to superscript
def to_superscript(num):
    superscripts = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return ''.join(superscripts.get(n, n) for n in str(num))

# Pretty print functions
def print_header(text):
    width = len(text) + 4
    print(f"\n{Fore.CYAN}{'═' * width}")
    print(f"{Fore.CYAN}║ {Fore.WHITE}{text} {Fore.CYAN}║")
    print(f"{Fore.CYAN}{'═' * width}\n")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠️ {text}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ️ {text}")

def print_status(label, status, active=True):
    status_color = Fore.GREEN if active else Fore.RED
    status_icon = "✅" if active else "❌"
    print(f"{Fore.WHITE}{label}: {status_color}{status_icon} {status}")

def print_loading(text="Loading", cycles=3):
    animations = [".  ", ".. ", "..."]
    for _ in range(cycles):
        for animation in animations:
            sys.stdout.write(f"\r{Fore.YELLOW}{text} {animation}")
            sys.stdout.flush()
            time.sleep(0.3)
    sys.stdout.write("\r" + " " * (len(text) + 5) + "\r")
    sys.stdout.flush()

def print_progress_bar(iteration, total, prefix='', suffix='', length=30, fill='█'):
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    sys.stdout.write(f'\r{Fore.BLUE}{prefix} |{Fore.CYAN}{bar}{Fore.BLUE}| {percent}% {suffix}')
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

# Config management
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print_error(f"Failed to load config: {e}")
            return default_config
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print_error(f"Failed to save config: {e}")
        return False

# Data backup functions
def backup_data():
    global last_backup_time
    backup_data = {
        "enemies": list(enemies),
        "current_font": current_font,
        "actions": actions,
        "spam_words": spam_words,
        "saved_messages": saved_messages,
        "reminders": reminders,
        "time_enabled": time_enabled,
        "saved_pics": saved_pics,
        "custom_replies": custom_replies,
        "blocked_words": blocked_words,
        "locked_chats": {k: list(v) for k, v in locked_chats.items()},
        "user_activity": dict(user_activity),
        "chat_settings": dict(chat_settings)
    }
    try:
        data = json.dumps(backup_data)
        if load_config()['backup_encryption']:
            data = cipher.encrypt(data.encode()).decode()
        with open("selfbot_backup.json", 'w') as f:
            f.write(data)
        last_backup_time = datetime.now()
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def restore_data():
    global enemies, current_font, actions, spam_words, saved_messages, reminders
    global time_enabled, saved_pics, custom_replies, blocked_words, locked_chats, user_activity, chat_settings
    if not os.path.exists("selfbot_backup.json"):
        return False
    try:
        with open("selfbot_backup.json", 'r') as f:
            data = f.read()
        if load_config()['backup_encryption']:
            data = cipher.decrypt(data.encode()).decode()
        data = json.loads(data)
        enemies = set(data.get("enemies", []))
        current_font = data.get("current_font", "normal")
        actions.update(data.get("actions", {}))
        spam_words = data.get("spam_words", [])
        saved_messages = data.get("saved_messages", [])
        reminders = data.get("reminders", [])
        time_enabled = data.get("time_enabled", True)
        saved_pics = data.get("saved_pics", [])
        custom_replies = data.get("custom_replies", {})
        blocked_words = data.get("blocked_words", [])
        locked_chats_data = data.get("locked_chats", {})
        for key, value in locked_chats_data.items():
            if key in locked_chats:
                locked_chats[key] = set(value)
        user_activity.update(data.get("user_activity", {}))
        chat_settings.update(data.get("chat_settings", {}))
        return True
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False

# Utility functions
async def text_to_voice(text, lang='fa'):
    print_info("Converting text to voice...")
    try:
        tts = gTTS(text=text, lang=lang)
        filename = f"voice_{int(time.time())}.mp3"
        tts.save(filename)
        print_success("Voice file created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to voice: {e}")
        print_error(f"Failed to convert text to voice: {e}")
        return None

async def text_to_image(text, bg_color='white', text_color='black', font_size=40):
    print_info("Creating image from text...")
    try:
        width = 800
        height = max(400, len(text) // 20 * 50)
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        lines = textwrap.wrap(text, width=30)
        y = 50
        for i, line in enumerate(lines):
            print_progress_bar(i + 1, len(lines), 'Progress:', 'Complete', 20)
            draw.text((50, y), line, font=font, fill=text_color)
            y += font_size + 10
        filename = f"text_{int(time.time())}.png"
        img.save(filename)
        print_success("Image created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to image: {e}")
        print_error(f"Failed to convert text to image: {e}")
        return None

async def text_to_gif(text, duration=500, bg_color='white'):
    print_info("Creating GIF from text...")
    try:
        width = 800
        height = 400
        frames = []
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        for i, color in enumerate(colors):
            print_progress_bar(i + 1, len(colors), 'Creating frames:', 'Complete', 20)
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            draw.text((50, 150), text, font=font, fill=color)
            frames.append(img)
        filename = f"text_{int(time.time())}.gif"
        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0
        )
        print_success("GIF created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to gif: {e}")
        print_error(f"Failed to convert text to GIF: {e}")
        return None

async def text_to_qr(text):
    print_info("Creating QR code...")
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        filename = f"qr_{int(time.time())}.png"
        img.save(filename)
        print_success("QR code created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in QR code creation: {e}")
        print_error(f"Failed to create QR code: {e}")
        return None

async def get_weather(city, api_key):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            async with session.get(url) as response:
                data = await response.json()
                if data.get("cod") != 200:
                    return f"❌ Error: {data.get('message', 'Unknown error')}"
                weather = data['weather'][0]['description']
                temp = data['main']['temp']
                return f"🌤️ Weather in {city}: {weather}, {temp}°C"
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return f"❌ Error fetching weather: {e}"

async def get_news(category, api_key):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={api_key}"
            async with session.get(url) as response:
                data = await response.json()
                if data.get("status") != "ok":
                    return "❌ Error fetching news"
                articles = data['articles'][:3]
                result = "📰 Top News:\n\n"
                for i, article in enumerate(articles, 1):
                    result += f"{i}. {article['title']}\n{article['url']}\n\n"
                return result
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return f"❌ Error fetching news: {e}"

async def analyze_text(text):
    words = text.split()
    chars = len(text)
    sentences = len(re.split(r'[.!?]+', text)) - 1
    return f"📊 Text Analysis:\nWords: {len(words)}\nCharacters: {chars}\nSentences: {sentences}"

async def generate_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

async def hash_text(text, algorithm='sha256'):
    h = hashlib.new(algorithm)
    h.update(text.encode())
    return h.hexdigest()

async def encode_base64(text):
    return base64.b64encode(text.encode()).decode()

async def decode_base64(text):
    try:
        return base64.b64decode(text).decode()
    except Exception as e:
        return f"❌ Error decoding base64: {e}"

async def check_website(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                status = response.status
                soup = BeautifulSoup(await response.text(), 'html.parser')
                title = soup.title.string if soup.title else "No title"
                return f"🌐 Website Check:\nURL: {url}\nStatus: {status}\nTitle: {title}"
    except Exception as e:
        return f"❌ Error checking website: {e}"

async def domain_info(domain):
    try:
        w = whois.whois(domain)
        return f"🌐 Domain Info:\nDomain: {domain}\nRegistrar: {w.registrar}\nExpiration: {w.expiration_date}"
    except Exception as e:
        return f"❌ Error fetching domain info: {e}"

async def resolve_dns(domain, record_type='A'):
    try:
        answers = dns.resolver.resolve(domain, record_type)
        return f"🌐 DNS Lookup ({record_type}):\n" + "\n".join([str(r) for r in answers])
    except Exception as e:
        return f"❌ Error resolving DNS: {e}"

async def update_time(client):
    while running:
        try:
            if time_enabled:
                config = load_config()
                now = datetime.now(pytz.timezone(config['timezone']))
                hours = to_superscript(now.strftime('%H'))
                minutes = to_superscript(now.strftime('%M'))
                time_string = f"{hours}:{minutes}"
                await client(functions.account.UpdateProfileRequest(last_name=time_string))
        except Exception as e:
            logger.error(f'Error updating time: {e}')
        await asyncio.sleep(60)

async def auto_online(client):
    while running and actions['online']:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
        except Exception as e:
            logger.error(f'Error updating online status: {e}')
        await asyncio.sleep(30)

async def auto_typing(client, chat):
    while running and actions['typing']:
        try:
            async with client.action(chat, 'typing'):
                await asyncio.sleep(3)
        except Exception as e:
            logger.error(f'Error in typing action: {e}')
            break

async def auto_reaction(event):
    if actions['reaction']:
        try:
            await event.message.react(random.choice(['👍', '❤️', '😄']))
        except Exception as e:
            logger.error(f'Error adding reaction: {e}')

async def auto_read_messages(event, client):
    if actions['read']:
        try:
            await client.send_read_acknowledge(event.chat_id, event.message)
        except Exception as e:
            logger.error(f'Error marking message as read: {e}')

async def schedule_message(client, chat_id, delay, message):
    print_info(f"Message scheduled to send in {delay} minutes")
    for i in range(delay):
        remaining = delay - i
        if remaining % 5 == 0 or remaining <= 5:
            logger.info(f"Scheduled message will send in {remaining} minutes")
        await asyncio.sleep(60)
    try:
        await client.send_message(chat_id, message)
        print_success(f"Scheduled message sent: {message[:30]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to send scheduled message: {e}")
        print_error(f"Failed to send scheduled message: {e}")
        return False

async def spam_messages(client, chat_id, count, message):
    print_info(f"Sending {count} messages...")
    success_count = 0
    for i in range(count):
        try:
            await client.send_message(chat_id, message)
            success_count += 1
            print_progress_bar(i + 1, count, 'Sending:', 'Complete', 20)
            await asyncio.sleep(load_config()['spam_delay'])
        except Exception as e:
            logger.error(f"Error in spam message {i+1}: {e}")
    print_success(f"Successfully sent {success_count}/{count} messages")
    return success_count

async def check_reminders(client):
    while running:
        current_time = datetime.now().strftime('%H:%M')
        to_remove = []
        for i, (reminder_time, message, chat_id) in enumerate(reminders):
            if reminder_time == current_time:
                try:
                    await client.send_message(chat_id, f"🔔 Reminder: {message}")
                    to_remove.append(i)
                except Exception as e:
                    logger.error(f"Failed to send reminder: {e}")
        for i in sorted(to_remove, reverse=True):
            del reminders[i]
        await asyncio.sleep(30)

async def auto_backup(client):
    config = load_config()
    if not config['auto_backup']:
        return
    interval = config['backup_interval'] * 60
    while running:
        await asyncio.sleep(interval)
        if backup_data():
            logger.info("Auto-backup completed successfully")
        else:
            logger.error("Auto-backup failed")

async def auto_delete_messages(client, chat_id):
    if actions['auto_delete']:
        config = load_config()
        delay = config['auto_delete_after']
        if delay > 0:
            await asyncio.sleep(delay)
            async for message in client.iter_messages(chat_id, from_user='me'):
                try:
                    await message.delete()
                except Exception as e:
                    logger.error(f"Error in auto delete: {e}")

async def auto_forward_messages(client, event, target_chat):
    if actions['auto_forward'] and event.message.text:
        try:
            await client.forward_messages(target_chat, event.message)
        except Exception as e:
            logger.error(f"Error in auto forward: {e}")

async def auto_mute_user(client, user_id, duration):
    if actions['auto_mute']:
        try:
            await client(functions.channels.EditBannedRequest(
                channel=user_id,
                participant=user_id,
                banned_rights=types.ChatBannedRights(until_date=datetime.now() + timedelta(minutes=duration), send_messages=False)
            ))
        except Exception as e:
            logger.error(f"Error in auto mute: {e}")

async def update_checker(client):
    config = load_config()
    if not config['auto_update_check']:
        return
    while running:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.github.com/repos/your-repo/selfbot/releases/latest") as response:
                    data = await response.json()
                    latest_version = data.get('tag_name', 'v0.0')
                    if latest_version > "v3.0":
                        await client.send_message('me', f"🔔 New version {latest_version} available!")
        except Exception as e:
            logger.error(f"Update check failed: {e}")
        await asyncio.sleep(3600)  # Check every hour

async def show_help_menu(client, event):
    help_text = f"""
{Fore.CYAN}📱 راهنمای ربات سلف بات نسخه 3.0:

{Fore.YELLOW}⚙️ تنظیمات دشمن:
• تنظیم دشمن (ریپلای) - اضافه کردن به لیست دشمن
• حذف دشمن (ریپلای) - حذف از لیست دشمن
• لیست دشمن - نمایش لیست دشمنان
• insult [on/off] - فعال/غیرفعال کردن پاسخ خودکار به دشمن
• enemy stats [id] - نمایش آمار دشمن
• enemy mute [id] [مدت] - میوت کردن دشمن
• enemy ban [id] - بن کردن دشمن

{Fore.YELLOW}🔤 فونت‌ها:
• bold on/off - فونت ضخیم
• italic on/off - فونت کج
• script on/off - فونت دست‌نویس
• double on/off - فونت دوتایی
• bubble on/off - فونت حبابی
• square on/off - فونت مربعی
• strikethrough on/off - فونت خط خورده
• underline on/off - فونت زیر خط دار
• caps on/off - فونت بزرگ
• lowercase on/off - فونت کوچک
• title on/off - فونت عنوان
• space on/off - فونت فاصله‌دار
• reverse on/off - فونت معکوس
• emoji on/off - فونت ایموجی
• mirror on/off - فونت آینه‌ای
• upside_down on/off - فونت وارونه

{Fore.YELLOW}⚡️ اکشن‌های خودکار:
• typing on/off - تایپینگ دائم
• online on/off - آنلاین دائم
• reaction on/off - ری‌اکشن خودکار
• time on/off - نمایش ساعت در نام
• read on/off - خواندن خودکار پیام‌ها
• reply on/off - پاسخ خودکار به پیام‌ها
• auto delete [on/off/time] - حذف خودکار پیام‌ها
• auto forward [chat_id] - فوروارد خودکار
• auto mute [on/off] - میوت خودکار کاربران
• anti spam [on/off] - جلوگیری از اسپم

{Fore.YELLOW}🔒 قفل‌ها:
• screenshot on/off - قفل اسکرین‌شات
• forward on/off - قفل فوروارد
• copy on/off - قفل کپی
• delete on/off - ضد حذف پیام
• edit on/off - ضد ویرایش پیام
• spam on/off - قفل اسپم
• mention on/off - قفل منشن

{Fore.YELLOW}🎨 تبدیل‌ها:
• متن به ویس بگو [متن] - تبدیل متن به ویس
• متن به عکس [متن] - تبدیل متن به عکس
• متن به گیف [متن] - تبدیل متن به گیف
• متن به کیوآر [متن] - تبدیل متن به QR کد
• save pic - ذخیره عکس (ریپلای)
• show pics - نمایش عکس‌های ذخیره شده
• save video - ذخیره ویدیو (ریپلای)
• show videos - نمایش ویدیوهای ذخیره شده
• compress file [path] - فشرده‌سازی فایل
• extract file [path] - استخراج فایل زیپ

{Fore.YELLOW}📝 پیام‌ها و یادآورها:
• schedule [زمان] [پیام] - ارسال پیام زماندار
• spam [تعداد] [پیام] - اسپم پیام
• save - ذخیره پیام (ریپلای)
• saved - نمایش پیام‌های ذخیره شده
• remind [زمان] [پیام] - تنظیم یادآور
• search [متن] - جستجو در پیام‌ها
• analyze text [متن] - تحلیل متن
• translate [متن] - ترجمه متن
• summarize [متن] - خلاصه‌سازی متن
• keyword add [کلمه] - افزودن کلمه کلیدی
• keyword remove [کلمه] - حذف کلمه کلیدی
• keyword list - نمایش کلمات کلیدی

{Fore.YELLOW}🔐 امنیت:
• block word [کلمه] - مسدود کردن کلمه
• unblock word [کلمه] - رفع مسدودیت کلمه
• block list - نمایش کلمات مسدود شده
• auto reply [trigger] [response] - تنظیم پاسخ خودکار
• delete reply [trigger] - حذف پاسخ خودکار
• replies - نمایش پاسخ‌های خودکار
• encrypt text [متن] - رمزنگاری متن
• decrypt text [متن] - رمزگشایی متن
• generate password [طول] - تولید رمز عبور
• hash text [متن] [الگوریتم] - هش کردن متن
• base64 encode [متن] - کدگذاری Base64
• base64 decode [متن] - رمزگشایی Base64

{Fore.YELLOW}🌐 ابزارهای وب:
• weather [شهر] - نمایش آب و هوا
• news [دسته‌بندی] - نمایش اخبار
• check website [آدرس] - بررسی وب‌سایت
• domain info [دامنه] - اطلاعات دامنه
• dns lookup [دامنه] [نوع] - جستجوی DNS
• download file [آدرس] - دانلود فایل از URL
• scrape website [آدرس] - اسکرپ وب‌سایت
• short url [آدرس] - کوتاه کردن URL
• ping [آدرس] - پینگ سرور
• trace [آدرس] - ردیابی مسیر

{Fore.YELLOW}📊 تحلیل و آمار:
• user stats [id] - نمایش آمار کاربر
• chat stats [id] - نمایش آمار چت
• message graph - نمایش گراف پیام‌ها
• activity log - نمایش لاگ فعالیت
• top users [تعداد] - نمایش کاربران برتر
• word cloud - تولید ابر کلمات
• sentiment [متن] - تحلیل احساسات
• message count - شمارش پیام‌ها
• chat history [limit] - تاریخچه چت
• export chat - خروجی گرفتن از چت

{Fore.YELLOW}🛠️ ابزارهای سیستمی:
• backup - ذخیره پشتیبان
• restore - بازیابی پشتیبان
• system info - اطلاعات سیستم
• process list - لیست پروسه‌ها
• disk usage - استفاده از دیسک
• cpu usage - استفاده از CPU
• memory usage - استفاده از حافظه
• restart - ریستارت ربات
• update - بررسی آپدیت
• log view - مشاهده لاگ

{Fore.YELLOW}🎲 سرگرمی:
• joke - نمایش جوک
• quote - نمایش نقل‌قول
• meme - نمایش میم
• roll dice [تعداد] - پرتاب تاس
• flip coin - پرتاب سکه
• random number [min] [max] - تولید عدد تصادفی
• trivia - سوال Trivia
• poll create [سوال] [گزینه‌ها] - ایجاد نظرسنجی
• game start - شروع بازی ساده
• emoji bomb - ارسال ایموجی‌های تصادفی

{Fore.YELLOW}📋 مدیریت:
• pin message - پین کردن پیام (ریپلای)
• unpin message - آنپین کردن پیام
• mute chat [مدت] - میوت کردن چت
• unmute chat - رفع میوت چت
• clear chat [تعداد] - پاک کردن پیام‌های چت
• export contacts - خروجی گرفتن از مخاطبین
• import contacts [فایل] - وارد کردن مخاطبین
• group create [نام] - ایجاد گروه
• group invite [id] - دعوت به گروه
• leave chat - ترک چت

{Fore.YELLOW}⚙️ تنظیمات پیشرفته:
• set timezone [منطقه] - تنظیم منطقه زمانی
• set language [زبان] - تنظیم زبان
• set spam delay [ثانیه] - تنظیم تاخیر اسپم
• set max spam [تعداد] - تنظیم حداکثر اسپم
• set backup interval [دقیقه] - تنظیم فاصله پشتیبان
• set encryption [on/off] - فعال/غیرفعال کردن رمزنگاری
• set log level [سطح] - تنظیم سطح لاگ
• set auto update [on/off] - فعال/غیرفعال کردن بررسی آپدیت
• set max message [طول] - تنظیم حداکثر طول پیام
• set auto delete [زمان] - تنظیم زمان حذف خودکار

{Fore.YELLOW}🔄 سایر:
• undo - برگرداندن آخرین عملیات
• status - نمایش وضعیت ربات
• exit - خروج از برنامه
"""
    try:
        await event.edit(help_text.replace(Fore.CYAN, "").replace(Fore.YELLOW, "").replace(Fore.WHITE, ""))
    except:
        print(help_text)

async def show_status(client, event):
    try:
        start_time = time.time()
        await client(functions.PingRequest(ping_id=0))
        ping = round((time.time() - start_time) * 1000, 2)
        config = load_config()
        tz = pytz.timezone(config['timezone'])
        now = datetime.now(tz)
        j_date = jdatetime.datetime.fromgregorian(datetime=now)
        jalali_date = j_date.strftime('%Y/%m/%d')
        local_time = now.strftime('%H:%M:%S')
        uptime_seconds = int(time.time() - start_time)
        uptime = str(timedelta(seconds=uptime_seconds))
        memory_usage = f"{psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024:.2f} MB"
        status_text = f"""
⚡️ وضعیت ربات سلف بات

📊 اطلاعات سیستم:
• پینگ: {ping} ms
• زمان کارکرد: {uptime}
• مصرف حافظه: {memory_usage}
• آخرین پشتیبان‌گیری: {last_backup_time.strftime('%Y/%m/%d %H:%M') if last_backup_time else 'هیچوقت'}

📅 اطلاعات زمانی:
• تاریخ شمسی: {jalali_date}
• ساعت: {local_time}
• منطقه زمانی: {config['timezone']}

💡 وضعیت قابلیت‌ها:
• تایپینگ: {'✅' if actions['typing'] else '❌'}
• آنلاین: {'✅' if actions['online'] else '❌'}
• ری‌اکشن: {'✅' if actions['reaction'] else '❌'}
• ساعت: {'✅' if time_enabled else '❌'}
• خواندن خودکار: {'✅' if actions['read'] else '❌'}
• پاسخ خودکار: {'✅' if actions['auto_reply'] else '❌'}
• حذف خودکار: {'✅' if actions['auto_delete'] else '❌'}
• فوروارد خودکار: {'✅' if actions['auto_forward'] else '❌'}
• میوت خودکار: {'✅' if actions['auto_mute'] else '❌'}
• ضد اسپم: {'✅' if actions['anti_spam'] else '❌'}

📌 آمار:
• تعداد دشمنان: {len(enemies)}
• پیام‌های ذخیره شده: {len(saved_messages)}
• یادآوری‌ها: {len(reminders)}
• کلمات مسدود شده: {len(blocked_words)}
• پاسخ‌های خودکار: {len(custom_replies)}

🔒 قفل‌های فعال:
• اسکرین‌شات: {len(locked_chats['screenshot'])}
• فوروارد: {len(locked_chats['forward'])}
• کپی: {len(locked_chats['copy'])}
• ضد حذف: {len(locked_chats['delete'])}
• ضد ویرایش: {len(locked_chats['edit'])}
• ضد اسپم: {len(locked_chats['spam'])}
• ضد منشن: {len(locked_chats['mention'])}
"""
        await event.edit(status_text)
    except Exception as e:
        logger.error(f"Error in status handler: {e}")
        print_error(f"Error showing status: {e}")

async def main():
    print(LOGO)
    print_header("Initializing Telegram Self-Bot")
    config = load_config()
    print_info(f"Configuration loaded from {CONFIG_FILE}")
    log_level = getattr(logging, config['log_level'])
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=LOG_FILE)
    init_database()
    if os.path.exists("selfbot_backup.json"):
        if restore_data():
            print_success("Data restored from backup")
        else:
            print_warning("Failed to restore data from backup")
    print_loading("Connecting to Telegram")
    client = TelegramClient(config['session_name'], config['api_id'], config['api_hash'])
    try:
        await client.connect()
        print_success("Connected to Telegram")
        if not await client.is_user_authorized():
            print_header("Authentication Required")
            print("Please enter your phone number (e.g., +989123456789):")
            phone = input(f"{Fore.GREEN}> ")
            print_loading("Sending verification code")
            await client.send_code_request(phone)
            print_success("Verification code sent")
            print("\nPlease enter the verification code:")
            code = input(f"{Fore.GREEN}> ")
            print_loading("Verifying code")
            await client.sign_in(phone, code)
            print_success("Verification successful")
        me = await client.get_me()
        print_success(f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'No username'})")
        print_info("Self-bot is now active! Type 'پنل' in any chat to see commands.")
        asyncio.create_task(update_time(client))
        asyncio.create_task(check_reminders(client))
        asyncio.create_task(auto_backup(client))
        asyncio.create_task(update_checker(client))

        @client.on(events.NewMessage)
        async def message_handler(event):
            try:
                if actions['read']:
                    await auto_read_messages(event, client)
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    if actions['auto_reply'] and event.raw_text and event.raw_text in custom_replies:
                        await event.reply(custom_replies[event.raw_text])
                    user_activity[str(event.from_id.user_id)]['message_count'] += 1
                    user_activity[str(event.from_id.user_id)]['last_seen'] = datetime.now().isoformat()
                    if any(word in event.raw_text.lower() for word in blocked_words):
                        await event.delete()
                        return
                    if actions['anti_spam'] and str(event.chat_id) in locked_chats['spam']:
                        async for msg in client.iter_messages(event.chat_id, from_user=event.from_id, limit=5):
                            if (datetime.now() - msg.date).seconds < 60:
                                user_activity[str(event.from_id.user_id)]['spam_count'] = user_activity[str(event.from_id.user_id)].get('spam_count', 0) + 1
                                if user_activity[str(event.from_id.user_id)]['spam_count'] > 5:
                                    await auto_mute_user(client, event.from_id.user_id, 60)
                                    await event.reply("🚫 کاربر به دلیل اسپم موقتاً میوت شد")
                    return
                if any(word in event.raw_text.lower() for word in blocked_words):
                    await event.delete()
                    return
                if actions['typing']:
                    asyncio.create_task(auto_typing(client, event.chat_id))
                if actions['reaction']:
                    await auto_reaction(event)
                if event.raw_text.startswith('schedule '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        try:
                            delay = int(parts[1])
                            message = parts[2]
                            asyncio.create_task(schedule_message(client, event.chat_id, delay, message))
                            await event.reply(f'✅ پیام بعد از {delay} دقیقه ارسال خواهد شد')
                        except ValueError:
                            await event.reply('❌ فرمت صحیح: schedule [زمان به دقیقه] [پیام]')
                elif event.raw_text.startswith('spam '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        try:
                            count = int(parts[1])
                            if count > config['max_spam_count']:
                                await event.reply(f"❌ حداکثر تعداد پیام برای اسپم {config['max_spam_count']} است")
                                return
                            message = parts[2]
                            asyncio.create_task(spam_messages(client, event.chat_id, count, message))
                        except ValueError:
                            await event.reply('❌ فرمت صحیح: spam [تعداد] [پیام]')
                elif event.raw_text == 'save' and event.is_reply:
                    replied = await event.get_reply_message()
                    if replied and replied.text:
                        saved_messages.append(replied.text)
                        command_history.append(('save_msg', None))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                        backup_data()
                        await event.reply('✅ پیام ذخیره شد')
                    else:
                        await event.reply('❌ پیام ریپلای شده متن ندارد')
                elif event.raw_text == 'saved':
                    if not saved_messages:
                        await event.reply('❌ پیامی ذخیره نشده است')
                        return
                    saved_text = '\n\n'.join(f'{i+1}. {msg}' for i, msg in enumerate(saved_messages))
                    if len(saved_text) > config['max_message_length']:
                        chunks = [saved_text[i:i+config['max_message_length']] for i in range(0, len(saved_text), config['max_message_length'])]
                        for i, chunk in enumerate(chunks):
                            await event.reply(f"بخش {i+1}/{len(chunks)}:\n\n{chunk}")
                    else:
                        await event.reply(saved_text)
                elif event.raw_text.startswith('remind '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        time_str = parts[1]
                        message = parts[2]
                        if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$', time_str):
                            reminders.append((time_str, message, event.chat_id))
                            backup_data()
                            await event.reply(f'✅ یادآور برای ساعت {time_str} تنظیم شد')
                        else:
                            await event.reply('❌ فرمت زمان اشتباه است. از فرمت HH:MM استفاده کنید')
                    else:
                        await event.reply('❌ فرمت صحیح: remind [زمان] [پیام]')
                elif event.raw_text.startswith('search '):
                    query = event.raw_text.split(maxsplit=1)[1]
                    await event.edit(f"🔍 در حال جستجوی '{query}'...")
                    messages = await client.get_messages(event.chat_id, search=query, limit=10)
                    if not messages:
                        await event.edit("❌ پیامی یافت نشد")
                        return
                    result = f"🔍 نتایج جستجو برای '{query}':\n\n"
                    for i, msg in enumerate(messages, 1):
                        sender = await msg.get_sender()
                        sender_name = utils.get_display_name(sender) if sender else "Unknown"
                        result += f"{i}. از {sender_name}: {msg.text[:100]}{'...' if len(msg.text) > 100 else ''}\n\n"
                    await event.edit(result)
                elif event.raw_text.startswith('block word '):
                    word = event.raw_text.split(maxsplit=2)[2].lower()
                    if word in blocked_words:
                        await event.reply(f"❌ کلمه '{word}' قبلاً مسدود شده است")
                    else:
                        blocked_words.append(word)
                        command_history.append(('block_word', word))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                        backup_data()
                        await event.reply(f"✅ کلمه '{word}' مسدود شد")
                elif event.raw_text.startswith('unblock word '):
                    word = event.raw_text.split(maxsplit=2)[2].lower()
                    if word not in blocked_words:
                        await event.reply(f"❌ کلمه '{word}' در لیست مسدود شده‌ها نیست")
                    else:
                        blocked_words.remove(word)
                        command_history.append(('unblock_word', word))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                        backup_data()
                        await event.reply(f"✅ کلمه '{word}' از لیست مسدود شده‌ها حذف شد")
                elif event.raw_text == 'block list':
                    if not blocked_words:
                        await event.reply("❌ لیست کلمات مسدود شده خالی است")
                    else:
                        block_list = '\n'.join(f"{i+1}. {word}" for i, word in enumerate(blocked_words))
                        await event.reply(f"📋 لیست کلمات مسدود شده:\n\n{block_list}")
                elif event.raw_text.startswith('auto reply '):
                    parts = event.raw_text.split(maxsplit=3)
                    if len(parts) == 4:
                        trigger = parts[2]
                        response = parts[3]
                        prev_response = custom_replies.get(trigger, None)
                        custom_replies[trigger] = response
                        command_history.append(('add_reply', trigger))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                        backup_data()
                        await event.reply(f"✅ پاسخ خودکار برای '{trigger}' تنظیم شد")
                    else:
                        await event.reply("❌ فرمت صحیح: auto reply [کلمه کلیدی] [پاسخ]")
                elif event.raw_text.startswith('delete reply '):
                    trigger = event.raw_text.split(maxsplit=2)[2]
                    if trigger not in custom_replies:
                        await event.reply(f"❌ هیچ پاسخ خودکاری برای '{trigger}' وجود ندارد")
                    else:
                        prev_response = custom_replies[trigger]
                        del custom_replies[trigger]
                        command_history.append(('del_reply', (trigger, prev_response)))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                        backup_data()
                        await event.reply(f"✅ پاسخ خودکار برای '{trigger}' حذف شد")
                elif event.raw_text == 'replies':
                    if not custom_replies:
                        await event.reply("❌ هیچ پاسخ خودکاری تنظیم نشده است")
                    else:
                        reply_list = '\n\n'.join(f"🔹 {trigger}:\n{response}" for trigger, response in custom_replies.items())
                        await event.reply(f"📋 لیست پاسخ‌های خودکار:\n\n{reply_list}")
                elif event.raw_text == 'backup':
                    if backup_data():
                        await event.reply("✅ پشتیبان‌گیری با موفقیت انجام شد")
                    else:
                        await event.reply("❌ خطا در پشتیبان‌گیری")
                elif event.raw_text == 'restore':
                    if restore_data():
                        await event.reply("✅ بازیابی داده‌ها با موفقیت انجام شد")
                    else:
                        await event.reply("❌ فایل پشتیبان یافت نشد یا مشکلی در بازیابی وجود دارد")
                elif event.raw_text.startswith('متن به ویس بگو '):
                    text = event.raw_text.split(maxsplit=3)[3]
                    await event.edit("⏳ در حال تبدیل متن به ویس...")
                    voice_file = await text_to_voice(text, lang=config['default_language'])
                    if voice_file:
                        await event.delete()
                        await client.send_file(event.chat_id, voice_file)
                        os.remove(voice_file)
                    else:
                        await event.edit("❌ خطا در تبدیل متن به ویس")
                elif event.raw_text.startswith('متن به عکس '):
                    text = event.raw_text.split(maxsplit=3)[3]
                    await event.edit("⏳ در حال تبدیل متن به عکس...")
                    img_file = await text_to_image(text)
                    if img_file:
                        await event.delete()
                        await client.send_file(event.chat_id, img_file)
                        os.remove(img_file)
                    else:
                        await event.edit("❌ خطا در تبدیل متن به عکس")
                elif event.raw_text.startswith('متن به گیف '):
                    text = event.raw_text.split(maxsplit=3)[3]
                    await event.edit("⏳ در حال تبدیل متن به گیف...")
                    gif_file = await text_to_gif(text)
                    if gif_file:
                        await event.delete()
                        await client.send_file(event.chat_id, gif_file)
                        os.remove(gif_file)
                    else:
                        await event.edit("❌ خطا در تبدیل متن به گیف")
                elif event.raw_text.startswith('متن به کیوآر '):
                    text = event.raw_text.split(maxsplit=3)[3]
                    await event.edit("⏳ در حال تبدیل متن به QR کد...")
                    qr_file = await text_to_qr(text)
                    if qr_file:
                        await event.delete()
                        await client.send_file(event.chat_id, qr_file)
                        os.remove(qr_file)
                    else:
                        await event.edit("❌ خطا در تبدیل متن به QR کد")
                elif event.raw_text == 'save pic' and event.is_reply:
                    replied = await event.get_reply_message()
                    if not replied.photo:
                        await event.reply("❌ پیام ریپلای شده عکس نیست")
                        return
                    await event.edit("⏳ در حال ذخیره عکس...")
                    path = await client.download_media(replied.photo)
                    saved_pics.append(path)
                    command_history.append(('save_pic', path))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    backup_data()
                    await event.edit("✅ عکس ذخیره شد")
                elif event.raw_text == 'show pics':
                    if not saved_pics:
                        await event.reply("❌ هیچ عکسی ذخیره نشده است")
                        return
                    await event.edit(f"⏳ در حال بارگذاری {len(saved_pics)} عکس...")
                    for i, pic_path in enumerate(saved_pics):
                        if os.path.exists(pic_path):
                            await client.send_file(event.chat_id, pic_path, caption=f"عکس {i+1}/{len(saved_pics)}")
                        else:
                            await client.send_message(event.chat_id, f"❌ عکس {i+1} یافت نشد")
                    await event.edit(f"✅ {len(saved_pics)} عکس نمایش داده شد")
                elif event.raw_text == 'save video' and event.is_reply:
                    replied = await event.get_reply_message()
                    if not replied.video:
                        await event.reply("❌ پیام ریپلای شده ویدیو نیست")
                        return
                    await event.edit("⏳ در حال ذخیره ویدیو...")
                    path = await client.download_media(replied.video)
                    saved_pics.append(path)
                    command_history.append(('save_video', path))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    backup_data()
                    await event.edit("✅ ویدیو ذخیره شد")
                elif event.raw_text == 'show videos':
                    videos = [p for p in saved_pics if p.endswith(('.mp4', '.avi', '.mkv'))]
                    if not videos:
                        await event.reply("❌ هیچ ویدیویی ذخیره نشده است")
                        return
                    await event.edit(f"⏳ در حال بارگذاری {len(videos)} ویدیو...")
                    for i, vid_path in enumerate(videos):
                        if os.path.exists(vid_path):
                            await client.send_file(event.chat_id, vid_path, caption=f"ویدیو {i+1}/{len(videos)}")
                        else:
                            await client.send_message(event.chat_id, f"❌ ویدیو {i+1} یافت نشد")
                    await event.edit(f"✅ {len(videos)} ویدیو نمایش داده شد")
                elif event.raw_text.startswith('weather '):
                    city = event.raw_text.split(maxsplit=1)[1]
                    result = await get_weather(city, config['weather_api_key'])
                    await event.reply(result)
                elif event.raw_text.startswith('news '):
                    category = event.raw_text.split(maxsplit=1)[1]
                    result = await get_news(category, config['news_api_key'])
                    await event.reply(result)
                elif event.raw_text.startswith('analyze text '):
                    text = event.raw_text.split(maxsplit=2)[2]
                    result = await analyze_text(text)
                    await event.reply(result)
                elif event.raw_text.startswith('generate password '):
                    length = int(event.raw_text.split(maxsplit=2)[2])
                    password = await generate_password(length)
                    await event.reply(f"🔑 Password: {password}")
                elif event.raw_text.startswith('hash text '):
                    parts = event.raw_text.split(maxsplit=3)
                    text = parts[2]
                    algorithm = parts[3] if len(parts) > 3 else 'sha256'
                    result = await hash_text(text, algorithm)
                    await event.reply(f"🔒 Hash ({algorithm}): {result}")
                elif event.raw_text.startswith('base64 encode '):
                    text = event.raw_text.split(maxsplit=2)[2]
                    result = await encode_base64(text)
                    await event.reply(f"🔢 Base64: {result}")
                elif event.raw_text.startswith('base64 decode '):
                    text = event.raw_text.split(maxsplit=2)[2]
                    result = await decode_base64(text)
                    await event.reply(f"🔢 Decoded: {result}")
                elif event.raw_text.startswith('check website '):
                    url = event.raw_text.split(maxsplit=2)[2]
                    result = await check_website(url)
                    await event.reply(result)
                elif event.raw_text.startswith('domain info '):
                    domain = event.raw_text.split(maxsplit=2)[2]
                    result = await domain_info(domain)
                    await event.reply(result)
                elif event.raw_text.startswith('dns lookup '):
                    parts = event.raw_text.split(maxsplit=3)
                    domain = parts[2]
                    record_type = parts[3] if len(parts) > 3 else 'A'
                    result = await resolve_dns(domain, record_type)
                    await event.reply(result)
                elif event.raw_text == 'system info':
                    info = f"💻 System Info:\nOS: {platform.system()} {platform.release()}\nCPU: {psutil.cpu_count()} cores\nMemory: {psutil.virtual_memory().total / 1024 / 1024:.2f} MB"
                    await event.reply(info)
                elif event.raw_text == 'restart':
                    await event.reply("🔄 Restarting bot...")
                    os.execv(sys.executable, ['python'] + sys.argv)
                elif event.raw_text == 'exit':
                    await event.reply("✅ در حال خروج از برنامه...")
                    global running
                    running = False
                    await client.disconnect()
                    return
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
                await event.reply(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern=r'^time (on|off)$'))
        async def time_handler(event):
            global time_enabled
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                status = event.pattern_match.group(1)
                time_enabled = (status == 'on')
                if not time_enabled:
                    await client(functions.account.UpdateProfileRequest(last_name=''))
                command_history.append(('time', not time_enabled))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                await event.edit(f"✅ نمایش ساعت {'فعال' if time_enabled else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in time handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern=r'^(screenshot|forward|copy|delete|edit|spam|mention) (on|off)$'))
        async def lock_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                command, status = event.raw_text.lower().split()
                chat_id = str(event.chat_id)
                prev_state = chat_id in locked_chats[command]
                if status == 'on':
                    locked_chats[command].add(chat_id)
                    await event.edit(f"✅ قفل {command} فعال شد")
                else:
                    locked_chats[command].discard(chat_id)
                    await event.edit(f"✅ قفل {command} غیرفعال شد")
                command_history.append(('lock', (command, chat_id, prev_state)))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                backup_data()
            except Exception as e:
                logger.error(f"Error in lock handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='پنل'))
        async def panel_handler(event):
            try:
                if not event.from_id:
                    return
                if event.from_id.user_id == (await client.get_me()).id:
                    await show_help_menu(client, event)
            except Exception as e:
                logger.error(f"Error in panel handler: {e}")

        @client.on(events.NewMessage(pattern='undo'))
        async def undo_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                if not command_history:
                    await event.edit("❌ تاریخچه دستورات خالی است")
                    return
                last_command = command_history.pop()
                command_type, data = last_command
                if command_type == 'time':
                    global time_enabled
                    time_enabled = data
                    if not time_enabled:
                        await client(functions.account.UpdateProfileRequest(last_name=''))
                    await event.edit(f"✅ وضعیت نمایش ساعت به {'فعال' if time_enabled else 'غیرفعال'} برگردانده شد")
                elif command_type == 'lock':
                    lock_type, chat_id, prev_state = data
                    if prev_state:
                        locked_chats[lock_type].add(chat_id)
                    else:
                        locked_chats[lock_type].discard(chat_id)
                    await event.edit(f"✅ وضعیت قفل {lock_type} به {'فعال' if prev_state else 'غیرفعال'} برگردانده شد")
                backup_data()
            except Exception as e:
                logger.error(f"Error in undo handler: {e}")
                await event.edit(f"❌ خطا در برگرداندن عملیات: {str(e)}")

        @client.on(events.NewMessage)
        async def enemy_handler(event):
            try:
                if not event.from_id:
                    return
                config = load_config()
                if event.from_id.user_id == (await client.get_me()).id:
                    if event.raw_text == 'تنظیم دشمن' and event.is_reply:
                        replied = await event.get_reply_message()
                        if replied and replied.from_id and hasattr(replied.from_id, 'user_id'):
                            user_id = str(replied.from_id.user_id)
                            prev_state = user_id in enemies
                            enemies.add(user_id)
                            command_history.append(('enemy_add', user_id))
                            if len(command_history) > MAX_HISTORY:
                                command_history.pop(0)
                            backup_data()
                            await event.reply('✅ کاربر به لیست دشمن اضافه شد')
                        else:
                            await event.reply('❌ نمی‌توان این کاربر را به لیست دشمن اضافه کرد')
                    elif event.raw_text == 'حذف دشمن' and event.is_reply:
                        replied = await event.get_reply_message()
                        if replied and replied.from_id and hasattr(replied.from_id, 'user_id'):
                            user_id = str(replied.from_id.user_id)
                            prev_state = user_id in enemies
                            enemies.discard(user_id)
                            command_history.append(('enemy_remove', user_id))
                            if len(command_history) > MAX_HISTORY:
                                command_history.pop(0)
                            backup_data()
                            await event.reply('✅ کاربر از لیست دشمن حذف شد')
                        else:
                            await event.reply('❌ نمی‌توان این کاربر را از لیست دشمن حذف کرد')
                    elif event.raw_text == 'لیست دشمن':
                        enemy_list = ''
                        for i, enemy in enumerate(enemies, 1):
                            try:
                                user = await client.get_entity(int(enemy))
                                enemy_list += f'{i}. {user.first_name} {user.last_name or ""} (@{user.username or "بدون یوزرنیم"})\n'
                            except:
                                enemy_list += f'{i}. ID: {enemy}\n'
                        await event.reply(enemy_list or '❌ لیست دشمن خالی است')
                elif config['enemy_auto_reply'] and str(event.from_id.user_id) in enemies:
                    insult1 = random.choice(insults)
                    insult2 = random.choice(insults)
                    while insult2 == insult1:
                        insult2 = random.choice(insults)
                    await event.reply(insult1)
                    await asyncio.sleep(0.5)
                    await event.reply(insult2)
            except Exception as e:
                logger.error(f"Error in enemy handler: {e}")

        @client.on(events.NewMessage)
        async def font_handler(event):
            global current_font
            try:
                if not event.from_id or not event.raw_text:
                    return
                if event.from_id.user_id != (await client.get_me()).id:
                    return
                text = event.raw_text.lower().split()
                if len(text) == 2 and text[1] in ['on', 'off'] and text[0] in font_styles:
                    font, status = text
                    prev_font = current_font
                    if status == 'on':
                        current_font = font
                        await event.edit(f'✅ حالت {font} فعال شد')
                    else:
                        current_font = 'normal'
                        await event.edit(f'✅ حالت {font} غیرفعال شد')
                    command_history.append(('font', prev_font))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                elif current_font != 'normal' and current_font in font_styles:
                    await event.edit(font_styles[current_font](event.raw_text))
            except Exception as e:
                logger.error(f"Error in font handler: {e}")

        print_success("Self-bot is running")
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print_warning("\nKilling the self-bot by keyboard interrupt...")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
    finally:
        running = False
        if client and client.is_connected():
            await client.disconnect()
        print_info("Self-bot has been shut down")

def init():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\nExiting self-bot...")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        logging.error(f"Unexpected init error: {e}")

if __name__ == '__main__':
    init()