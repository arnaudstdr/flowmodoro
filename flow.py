#!/usr/bin/env python3

import tkinter as tk
from collections import defaultdict
from tkinter import messagebox, scrolledtext, ttk
import time
import threading
import pygame
import json
from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt

#Initialize pygame mixer for playing sounds
pygame.mixer.init()

# Global variables
current_session_counter = 0
session_file = "sessions.json"
categories = ["Formation", "Freelance", "Projets", "Perso", "KCS"]

# pushhover
user_key = "u4tks68bo8kd3pukj7tteu8g5pmwk6"
api_token = "agrfhyvzkhr7sgbqa5xa11hihms1vv"

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def send_push_notification(title, message):
    payload = {
        "token": api_token,
        "user": user_key,
        "title": title,
        "message": message,
    }
    response = response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
    if response.status_code == 200:
        print("Notification envoyée avec succès.")
    else:
        print(f"Erreur lors de l'envoi de la notification : {response.status_code} - {response.text}")


def start_work_session():
    global start_time, current_session_counter
    start_time = time.time()
    current_session_counter += 1
    update_session_count()
    work_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    update_timer()

def stop_work_session():
    global end_time, work_duration
    end_time = time.time()
    work_duration = end_time - start_time
    selected_category = category_combobox.get()
    save_session(start_time, end_time, work_duration, selected_category)
    work_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    break_duration = work_duration / 5
    break_minutes = break_duration / 60
    messagebox.showinfo("Break Time", f"Break Time : {break_minutes:.2f} minutes.")
    start_timer(break_duration)

def update_timer():
    if work_button['state'] == tk.DISABLED:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        root.after(1000, update_timer)

def start_timer(seconds):
    def countdown():
        nonlocal seconds
        while seconds > 0:
            minutes, seconds_remaining = divmod(int(seconds), 60)
            timer_label.config(text=f"{minutes:02d}:{seconds_remaining:02d}")
            time.sleep(1)
            seconds -= 1
        timer_label.config(text="00:00")
        play_sound('notification_sound.mp3')
        send_push_notification("Flowmodoro", "Time's up !")
        messagebox.showinfo("Time's up", "Time's up")

    timer_thread = threading.Thread(target=countdown)
    timer_thread.start()

def save_session(start_time, end_time, duration, category):
    start_datetime =  datetime.fromtimestamp(start_time)
    end_datetime = datetime.fromtimestamp(end_time)
    session_data = {
        "start_time": start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        "duration": duration,
        "category": category,
        "week_number": start_datetime.strftime('%Y-%W')
    }
    try:
        with open(session_file, "r") as file:
            sessions = json.load(file)
    except FileNotFoundError:
        sessions = []
    sessions.append(session_data)
    with open(session_file, "w") as file:
        json.dump(sessions, file)

def load_sessions():
    try:
        with open(session_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def show_history():
    sessions = load_sessions()
    history_window = tk.Toplevel(root)
    history_window.title("Daily History")

    text_area = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Regrouper les sessions par date
    sessions_by_date = defaultdict(list)
    for session in sessions:
        # Extraire la date de début de la session
        date = session['start_time'].split(' ')[0]
        sessions_by_date[date].append(session)

    # Générer le rapport pour chaque jour
    for date, daily_sessions in sessions_by_date.items():
        total_duration = sum(session['duration'] for session in daily_sessions)
        num_sessions = len(daily_sessions)

        # Afficher les statistiques journalières
        date_info = (f"Date : {date}\n"
                     f"Nombre de sessions : {num_sessions}\n"
                     f"Durée totale : {total_duration / 3600:.2f} heures\n")
        text_area.insert(tk.END, date_info)
        text_area.insert(tk.END, '='*60 + '\n')

    text_area.config(state=tk.DISABLED)

def show_weekly_analysis():
    sessions = load_sessions()
    weekly_data = defaultdict(lambda: {"session_count": 0, "total_duration": 0, "days": set()})

    for session in sessions:
        week_number = session["week_number"]
        duration = session["duration"]
        date = session['start_time'].split(' ')[0]

        weekly_data[week_number]["session_count"] += 1
        weekly_data[week_number]["total_duration"] += duration
        weekly_data[week_number]["days"].add(date)

    analysis_window = tk.Toplevel(root)
    analysis_window.title("Weekly Analysis")

    text_area = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    for week, data in sorted(weekly_data.items()):
        num_days = len(data["days"])
        average_daily_duration = (data["total_duration"] / num_days) / 3600 if num_days > 0 else 0

        week_info = (f"Semaine : {week}\n"
                     f"Nombre de sessions : {data['session_count']}\n"
                     f"Durée totale : {data['total_duration'] / 3600:.2f} heures\n"
                     f"Moyenne de travail par jour : {average_daily_duration:.2f} heures\n")
        text_area.insert(tk.END, week_info)
        text_area.insert(tk.END, '-'*60 + '\n')

    text_area.config(state=tk.DISABLED)

import matplotlib.pyplot as plt

def show_category_analysis_graph():
    sessions = load_sessions()

    # Regrouper les sessions par catégorie
    category_data = defaultdict(lambda: {"session_count": 0, "total_duration": 0})

    for session in sessions:
        category = session.get("category", "Unknown")
        duration = session["duration"]
        
        # Mise à jour des données de la catégorie
        category_data[category]["session_count"] += 1
        category_data[category]["total_duration"] += duration

    # Préparer les données pour le graphique
    categories = list(category_data.keys())
    total_hours = [data["total_duration"] / 3600 for data in category_data.values()]

    # Créer un graphique à barres
    plt.figure(figsize=(10, 6))
    plt.bar(categories, total_hours, color='skyblue')
    plt.xlabel('Catégories')
    plt.ylabel('Heures totales')
    plt.title('Temps total par catégorie')
    plt.show()

def update_session_count():
    session_count_label.config(text=f"Current Sessions: {current_session_counter}")

root = tk.Tk()
root.title("FlowModoro")

timer_label = tk.Label(root, text="00:00", font=("Helvetica", 48))
timer_label.pack(pady=20)

session_count_label = tk.Label(root, text=f"Current Session: {current_session_counter}", font=("Helvetica", 16))
session_count_label.pack(pady=10)

category_label = tk.Label(root, text="Select Category:", font=("Helvetica", 12))
category_label.pack(pady=10)

category_combobox = ttk.Combobox(root, values=categories, state="readonly")
category_combobox.set("Perso")  # Catégorie par défaut
category_combobox.pack(pady=10)

work_button = tk.Button(root, text="Start Work Session", command=start_work_session)
work_button.pack(side=tk.LEFT, padx=20)

stop_button = tk.Button(root, text="Stop Work Session", command=stop_work_session, state=tk.DISABLED)
stop_button.pack(side=tk.RIGHT, padx=20)

history_button = tk.Button(root, text="Daily History", command=show_history)
history_button.pack(pady=20)

analysis_button = tk.Button(root, text="Weekly Analysis", command=show_weekly_analysis)
analysis_button.pack(pady=10)

category_graph_button = tk.Button(root, text="Show Category Graph", command=show_category_analysis_graph)
category_graph_button.pack(pady=10)

root.mainloop()