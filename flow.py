#!/usr/bin/env python3

import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import messagebox, scrolledtext, filedialog
from collections import defaultdict
import time
import threading
import pygame
import json
import csv
from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY')
PUSHOVER_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN')

# Paramètres globaux
settings_file = "settings.json"

session_active = False

pygame.mixer.init()
# Fonctions de gestion des paramètres
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

# Charger les paramètres au démarrage
app_settings = load_settings()

# Global variables
current_session_counter = 0
session_file = "sessions.json"
categories = ["Formation 📚", "Pro 💼", "Perso🏠"]
task_file = "tasks.json"

# pushhover
# user_key = api.KEY
# api_token = api.TOKEN

def play_sound(file_path):
    if app_settings.get("sound_enabled", True):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

def send_push_notification(title, message):
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


def start_work_session():
    global start_time, current_session_counter, session_active
    start_time = time.time()
    current_session_counter += 1
    session_active = True  # Session en cours
    update_session_count()
    work_button.config(state=ttkb.DISABLED)
    stop_button.config(state=ttkb.NORMAL)
    update_timer()  # Premier appel explicite ici


def stop_work_session():
    global end_time, work_duration, session_active
    end_time = time.time()
    work_duration = end_time - start_time
    session_active = False  # Fin de la session
    selected_category = category_combobox.get()
    selected_task = task_combobox.get()
    save_session(start_time, end_time, work_duration, selected_category, selected_task)
    update_status(f"Session saved : {selected_task} ({selected_category})")
    work_button.config(state=ttkb.NORMAL)
    stop_button.config(state=ttkb.DISABLED)
    break_duration = work_duration / 5
    break_minutes = break_duration / 60
    messagebox.showinfo("Break Time", f"Break Time : {break_minutes:.2f} minutes.")
    start_timer(break_duration)

def update_timer():
    if session_active:  # Dépend explicitement de session_active
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        root.after(1000, update_timer)
    else:
        timer_label.config(text="00:00")

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

# Sauvegarde des sessions
def save_session(start_time, end_time, duration, category, task):
    start_datetime =  datetime.fromtimestamp(start_time)
    end_datetime = datetime.fromtimestamp(end_time)
    billable = is_billable.get()
    session_data = {
        "start_time": start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        "duration": duration,
        "category": category,
        "task": task,
        "billable": billable,
        "week_number": start_datetime.strftime('%Y-%W')
    }
    try:
        with open(session_file, "r") as file:
            sessions = json.load(file)
    except FileNotFoundError:
        sessions = []
    sessions.append(session_data)
    with open(session_file, "w") as file:
        json.dump(sessions, file, indent=4)

def load_sessions():
    try:
        with open(session_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
def update_status(message):
    status_label.config(text=message)
    root.after(5000, lambda: status_label.config(text=""))

# Tâchs
def load_tasks():
    try:
        with open(task_file, "r") as file:
            tasks = json.load(file)
            return tasks
    except FileNotFoundError:
        return []

def get_task_names():
    tasks = load_tasks()
    return sorted([task["name"] for task in tasks])

def save_task(task):
    tasks = load_tasks()
    billable = is_billable.get()
    task_data = {"name": task, "billable": billable}
    if task_data not in tasks:
        tasks.append(task_data)
        with open(task_file, "w") as file:
            json.dump(tasks, file, indent=2)

    # Réinitialiser la case à cocher après ajout
    is_billable.set(False)

def add_task():
    task = task_entry.get()
    if task:
        save_task(task)
        task_combobox['values'] = get_task_names()
        task_entry.delete(0, ttkb.END)
        update_status(f"Tâche '{task}' ajoutée.")
    else:
        update_status("Erreur : entrez une tâche avant d'ajouter.")

def delete_task():
    selected_task = task_combobox.get()
    if not selected_task or selected_task == "Select a task":
        update_status("Error: no task selected.")
        return

    tasks = load_tasks()
    updated_tasks = [task for task in tasks if task["name"] != selected_task]

    if len(updated_tasks) == len(tasks):
        update_status("Task not found.")
        return

    with open(task_file, "w") as file:
        json.dump(updated_tasks, file, indent=2)

    task_combobox['values'] = get_task_names()
    task_combobox.set("Select a task")
    update_status(f"Task '{selected_task}' deleted.")

# Chargement initial des tâches
existing_tasks = get_task_names()

def update_billable_status(event):
    selected_task = task_combobox.get()
    tasks = load_tasks()
    for task in tasks:
        if task["name"] == selected_task:
            is_billable.set(task["billable"])
            return
    is_billable.set(False)

    task_combobox.bind("<<ComboboxSelected>>", update_billable_status)

# Analyse du temps par tâche et catégories
def analyze_time_by_task_and_category():
    sessions = load_sessions()
    analysis_data = defaultdict(lambda: defaultdict(lambda: {"time": 0, "billable": 0}))

    for session in sessions:
        category = session["category"]
        task = session["task"]
        duration = session["duration"]
        billable = session.get("billable", False)

        analysis_data[category][task] ["time"] += duration
        if billable:
            analysis_data[category][task]["billable"] += duration

    # Afficher les résultats dans une nouvelle fenêtre
    analysis_window = ttkb.Toplevel(root)
    analysis_window.title("Analysis by Task and Category")

    text_area = scrolledtext.ScrolledText(analysis_window, wrap=ttkb.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10, fill=ttkb.BOTH, expand=True)

    for category, tasks in analysis_data.items():
        text_area.insert(ttkb.END, f"Catégorie : {category}\n")
        for task, data in tasks.items():
            text_area.insert(ttkb.END, f"  - Tâche : {task} -> {data['time'] / 3600:.2f} heures, Facturable : {data['billable']/3600:.2f} heures\n")
        text_area.insert(ttkb.END, "="*60 + "\n")

    text_area.config(state=ttkb.DISABLED)

def export_analysis_to_csv():
    sessions = load_sessions()
    analysis_data = defaultdict(lambda:defaultdict(lambda: {"time": 0, "billable": 0}))

    for session in sessions:
        category = session["category"]
        task = session["task"]
        duration = session["duration"]
        billable = session.get("billable", False)

        analysis_data[category][task]["time"] += duration
        if billable:
            analysis_data[category][task]["billable"] += duration

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save Analysis as CSV"
    )

    if file_path:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Catégorie", "Tâche", "Temps total (heures)", "Temps facturable (heures)"])

            for category, tasks in analysis_data.items():
                for task, data in tasks.items():
                    writer.writerow([
                        category,
                        task,
                        round(data["time"] / 3600, 2),
                        round(data["billable"] / 3600, 2)
                    ])
        messagebox.showinfo("Export terminé", f"Les données ont été exportées avec succès vers {file_path}.")

def show_history():
    sessions = load_sessions()
    history_window = ttkb.Toplevel(root)
    history_window.title("Daily History")

    text_area = scrolledtext.ScrolledText(history_window, wrap=ttkb.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10, fill=ttkb.BOTH, expand=True)

    # Regrouper les sessions par date
    sessions_by_date = defaultdict(list)
    for session in sessions:
        # Extraire la date de début de la session
        date = session['start_time'].split(' ')[0]
        sessions_by_date[date].append(session)

    # Générer le rapport pour chaque jour
    for date in sorted(sessions_by_date.keys(), reverse=True):
        daily_sessions = sessions_by_date[date]
        total_duration = sum(session['duration'] for session in daily_sessions)
        num_sessions = len(daily_sessions)

        # Afficher les statistiques journalières
        date_info = (f"Date : {date}\n"
                     f"Nombre de sessions : {num_sessions}\n"
                     f"Durée totale : {total_duration / 3600:.2f} heures\n")
        text_area.insert(ttkb.END, date_info)
        text_area.insert(ttkb.END, '='*60 + '\n')

    text_area.config(state=ttkb.DISABLED)

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

    analysis_window = ttkb.Toplevel(root)
    analysis_window.title("Weekly Analysis")

    text_area = scrolledtext.ScrolledText(analysis_window, wrap=ttkb.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10, fill=ttkb.BOTH, expand=True)

    for week, data in sorted(weekly_data.items(), reverse=True):
        num_days = len(data["days"])
        average_daily_duration = (data["total_duration"] / num_days) / 3600 if num_days > 0 else 0

        week_info = (f"Semaine : {week}\n"
                     f"Nombre de sessions : {data['session_count']}\n"
                     f"Durée totale : {data['total_duration'] / 3600:.2f} heures\n"
                     f"Moyenne de travail par jour : {average_daily_duration:.2f} heures\n")
        text_area.insert(ttkb.END, week_info)
        text_area.insert(ttkb.END, '-'*60 + '\n')

    text_area.config(state=ttkb.DISABLED)

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

    sessions = load_sessions()
    today = datetime.now().strftime('%Y-%m-%d')
    daily_duration = sum(session['duration'] for session in sessions if session['start_time'].startswith(today))
    
    hours, remainder = divmod(daily_duration, 3600)
    minutes, _ = divmod(remainder, 60)

    daily_hours_label.config(text=f"Today's work: {int(hours)}h {int(minutes)}m")

root = ttkb.Window(themename=app_settings.get("theme", "superhero"))
root.title("FlowModoro")

# Main frame central pour tous les widgets
main_frame = ttkb.Frame(root, padding=20)
main_frame.pack(expand=True)

status_label = ttkb.Label(root, text="", font=("Segoe UI", 10), anchor="w")
status_label.pack(fill="x", side="bottom", padx=10, pady=5)

# Ajout de la barre de menu Analysis et Settings
menubar = ttkb.Menu(root)

analysis_menu = ttkb.Menu(menubar, tearoff=0)
analysis_menu.add_command(label="Daily history", command=show_history)
analysis_menu.add_command(label="Weekly history", command=show_weekly_analysis)
analysis_menu.add_command(label="Task & Category Analysis", command=analyze_time_by_task_and_category)
analysis_menu.add_command(label="Graphics", command=show_category_analysis_graph)
analysis_menu.add_command(label="Export as CSV", command=export_analysis_to_csv)
menubar.add_cascade(label="Analysis", menu=analysis_menu)

# Menu Settings
def open_settings_window():
    settings_window = ttkb.Toplevel(root)
    settings_window.title("Settings")

    sound_var = ttkb.BooleanVar(value=app_settings.get("sound_enabled", True))
    pushover_var = ttkb.BooleanVar(value=app_settings.get("pushover_enabled", True))
    theme_var = ttkb.StringVar(value=app_settings.get("theme", "superhero"))
    reminder_var = ttkb.BooleanVar(value=app_settings.get("reminder_enabled", True))

    ttkb.Checkbutton(settings_window, text="Enable notification sound", variable=sound_var).pack(anchor="w", padx=10, pady=5)
    ttkb.Checkbutton(settings_window, text="Enable Pushover", variable=pushover_var).pack(anchor="w", padx=10, pady=5)
    ttkb.Checkbutton(settings_window, text="Reminder if no session for 10 min", variable=reminder_var).pack(anchor="w", padx=10, pady=5)

    ttkb.Label(settings_window, text="Thème").pack(anchor="w", padx=10, pady=5)
    themes = ["superhero", "darkly", "flatly", "minty", "cyborg", "journal", "solar"]
    ttkb.Combobox(settings_window, textvariable=theme_var, values=themes, state="readonly").pack(padx=10, pady=5)

    def save_and_close():
        app_settings["sound_enabled"] = sound_var.get()
        app_settings["pushover_enabled"] = pushover_var.get()
        app_settings["theme"] = theme_var.get()
        app_settings["reminder_enabled"] = reminder_var.get()
        save_settings(app_settings)
        messagebox.showinfo("Settings", "Saved settings. Please restart the application for changes to take effect.")
        settings_window.destroy()

    ttkb.Button(settings_window, text="Save", command=save_and_close, bootstyle="success").pack(pady=10)

settings_menu = ttkb.Menu(menubar, tearoff=0)
settings_menu.add_command(label="Settings", command=open_settings_window)
menubar.add_cascade(label="Settings", menu=settings_menu)

root.config(menu=menubar)

timer_label = ttkb.Label(main_frame, text="00:00", font=("Segoe UI", 48, "bold"))
timer_label.pack(pady=20)

session_count_label = ttkb.Label(main_frame, text=f"Current session : {current_session_counter}", font=("Segoe UI", 16, "bold"))
session_count_label.pack(pady=10)

daily_hours_label = ttkb.Label(main_frame, text="Today's work: 0h 0m", font=("Segoe UI", 14, "bold"))
daily_hours_label.pack(pady=5)

category_combobox = ttkb.Combobox(main_frame, values=categories, state="readonly", bootstyle="info")
category_combobox.set("Select a category")  # Catégorie par défaut
category_combobox.pack(pady=10)

task_combobox = ttkb.Combobox(main_frame, values=existing_tasks, state="readonly", bootstyle="secondary")
task_combobox.set("Select a task")  # Tâche par défaut
task_combobox.pack(pady=10)

is_billable = ttkb.BooleanVar()

billable_checkbox = ttkb.Checkbutton(main_frame, text="Billable 💰", variable=is_billable)
billable_checkbox.pack(pady=5)

task_label = ttkb.Label(main_frame, text="Add a task ✅:", font=("Segoe UI", 12, "bold"))
task_label.pack(pady=5)

task_entry = ttkb.Entry(main_frame, font=("Segoe UI", 12))
task_entry.pack(pady=5)

add_task_button = ttkb.Button(main_frame, text="✚ Add task", command=add_task, bootstyle="success")
add_task_button.pack(pady=5)

delete_task_button = ttkb.Button(main_frame, text="❌ Delete selected task", command=delete_task, bootstyle="danger")
delete_task_button.pack(pady=5)

# Séparateur vertical entre les deux colonnes
separator = ttkb.Separator(main_frame, orient="vertical")
separator.pack(side="left", fill="y", padx=10)

# Encapsuler les colonnes dans un bottom_frame
bottom_frame = ttkb.Frame(main_frame)
bottom_frame.pack(pady=10)

left_frame = ttkb.Frame(bottom_frame)
left_frame.pack(side="left", padx=10)

right_frame = ttkb.Frame(bottom_frame)
right_frame.pack(side="left", padx=10)

work_button = ttkb.Button(left_frame, text="🚀 Start Session", command=start_work_session, bootstyle="primary")
work_button.pack(pady=5)

stop_button = ttkb.Button(right_frame, text="⏹️ Stop Session", command=stop_work_session, state="disabled", bootstyle="warning")
stop_button.pack(pady=5)

# history_button = ttkb.Button(left_frame, text="Daily history", command=show_history, bootstyle="info")
# history_button.pack(pady=5)
#
# analysis_button = ttkb.Button(right_frame, text="Weekly history", command=show_weekly_analysis, bootstyle="info")
# analysis_button.pack(pady=5)
#
# task_category_analysis_button = ttkb.Button(left_frame, text="Task & Category Analysis", command=analyze_time_by_task_and_category, bootstyle="secondary")
# task_category_analysis_button.pack(pady=5)
#
# export_csv_button = ttkb.Button(right_frame, text="Export as CSV", command=export_analysis_to_csv, bootstyle="secondary")
# export_csv_button.pack(pady=5)

# category_graph_button = ttkb.Button(root, text="Graphics", command=show_category_analysis_graph, bootstyle="dark")
# category_graph_button.pack(pady=10)

# Rappel d'inactivité si activé
def check_for_inactivity():
    if work_button['state'] == ttkb.NORMAL and app_settings.get("reminder_enabled", True):
        send_push_notification("Flowmodoro", "N'oubliez pas de démarrer une session !")
    root.after(600000, check_for_inactivity)  # 10 minutes

check_for_inactivity()

root.mainloop()