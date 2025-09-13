import json
import os
from dotenv import load_dotenv

load_dotenv()
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY')
PUSHOVER_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN')

settings_file = "settings.json"
session_file = "sessions.json"
task_file = "tasks.json"
categories = ["Formation 📚", "Pro 💼", "Bénévolat 🤝", "Perso 🏠"]

def load_settings():
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "sound_enabled": True,
            "pushover_enabled": True,
            "theme": "superhero",
            "reminder_enabled": True
        }

def load_tasks():
    try:
        with open(task_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

app_settings = load_settings()
existing_tasks = [task["name"] for task in load_tasks()]
