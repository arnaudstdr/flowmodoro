import json
import requests
import pygame
from src.config import PUSHOVER_API_TOKEN, PUSHOVER_USER_KEY, settings_file

pygame.mixer.init()

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

def save_settings(settings):
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)

def play_sound(file_path, app_settings):
    if app_settings.get("sound_enabled", True):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

def send_push_notification(title, message, app_settings):
    if app_settings.get("pushover_enabled", True):
        payload = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "title": title,
            "message": message,
        }
        response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
        if response.status_code == 200:
            print("Notification envoyée avec succès.")
        else:
            print(f"Erreur lors de l'envoi de la notification : {response.status_code} - {response.text}")