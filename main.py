#!/usr/bin/env python3

import sys
import os

# Ajouter le répertoire src au chemin de recherche des modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ttkbootstrap as ttkb
from tkinter import messagebox, scrolledtext, filedialog
import time
import threading
import pygame
from datetime import datetime
import rumps
import subprocess
from pathlib import Path
TIMER_FILE = Path.home() / ".flowmodoro_timer"
# Handle menu bar subprocess so we can terminate it when GUI closes
menu_bar_process = None
BREAK_FILE = Path.home() / ".flowmodoro_break_timer"
from src.config import app_settings, categories, existing_tasks
from src.utils import load_settings, play_sound, send_push_notification
from src.tasks import get_task_names, add_task, delete_task
from src.sessions import load_sessions, save_session
from src.ui import open_settings_window
from src.analysis import analyze_time_by_task_and_category, export_analysis_to_csv, show_history, show_weekly_analysis, show_category_analysis_graph

# Charger les paramètres au démarrage
app_settings = load_settings()

# Global variables
current_session_counter = 0
session_active = False
pygame.mixer.init()

# macOS menu bar timer integration
class FlowModoroBar(rumps.App):
    def __init__(self):
        super().__init__("⏱️ Flow")
        self.title = "00:00"
        # Update every second
        self.timer = rumps.Timer(self.refresh, 1)
        self.timer.start()

    def refresh(self, _):
        # If a break timer is active, show countdown
        if BREAK_FILE.exists():
            end_ts = float(BREAK_FILE.read_text())
            remaining = end_ts - time.time()
            if remaining > 0:
                m, s = divmod(int(remaining), 60)
                self.title = f"{m:02d}:{s:02d}"
            else:
                BREAK_FILE.unlink()
                self.title = "00:00"
        # Otherwise if work session active, show elapsed
        elif TIMER_FILE.exists():
            start_ts = float(TIMER_FILE.read_text())
            elapsed = time.time() - start_ts
            m, s = divmod(int(elapsed), 60)
            self.title = f"{m:02d}:{s:02d}"
        else:
            self.title = "00:00"


def start_work_session():
    global start_time, current_session_counter, session_active
    start_time = time.time()
    current_session_counter += 1
    session_active = True  # Session en cours
    TIMER_FILE.write_text(str(start_time))
    update_session_count()
    work_button.config(state=ttkb.DISABLED)
    stop_button.config(state=ttkb.NORMAL)
    update_timer()  # Premier appel explicite ici

def stop_work_session():
    global end_time, work_duration, session_active
    end_time = time.time()
    work_duration = end_time - start_time
    session_active = False  # Fin de la session
    if TIMER_FILE.exists():
        TIMER_FILE.unlink()
    selected_category = category_combobox.get()
    selected_task = task_combobox.get()
    save_session(start_time, end_time, work_duration, selected_category, selected_task, is_billable)
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
    # Write break end timestamp for menu bar
    break_end_ts = time.time() + seconds
    BREAK_FILE.write_text(str(break_end_ts))
    def countdown():
        nonlocal seconds
        while seconds > 0:
            minutes, seconds_remaining = divmod(int(seconds), 60)
            timer_label.config(text=f"{minutes:02d}:{seconds_remaining:02d}")
            time.sleep(1)
            seconds -= 1
        timer_label.config(text="00:00")
        # Clean up break file when countdown finishes
        if BREAK_FILE.exists():
            BREAK_FILE.unlink()
        play_sound('notification_sound.mp3', app_settings)
        send_push_notification("Flowmodoro", "Fin de la pause ! On y retourne 💪", app_settings)
        messagebox.showinfo("Time's up", "Fin de la pause ! On y retourne 💪")

    timer_thread = threading.Thread(target=countdown)
    timer_thread.start()

def update_status(message):
    status_label.config(text=message)
    root.after(5000, lambda: status_label.config(text=""))

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
analysis_menu.add_command(label="Daily history", command=lambda: show_history(root))
analysis_menu.add_command(label="Weekly history", command=lambda: show_weekly_analysis(root))
analysis_menu.add_command(label="Task & Category Analysis", command=lambda: analyze_time_by_task_and_category(root))
analysis_menu.add_command(label="Graphics", command=lambda: show_category_analysis_graph(root))
analysis_menu.add_command(label="Export as CSV", command=lambda: export_analysis_to_csv(root))
menubar.add_cascade(label="Analysis", menu=analysis_menu)

# Menu Settings
settings_menu = ttkb.Menu(menubar, tearoff=0)
settings_menu.add_command(label="Settings", command=lambda: open_settings_window(root))
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

task_combobox = ttkb.Combobox(main_frame, values=get_task_names(), state="readonly", bootstyle="secondary")
task_combobox.set("Select a task")  # Tâche par défaut
task_combobox.pack(pady=10)

is_billable = ttkb.BooleanVar()

billable_checkbox = ttkb.Checkbutton(main_frame, text="Billable 💰", variable=is_billable)
billable_checkbox.pack(pady=5)

task_label = ttkb.Label(main_frame, text="Add a task ✅:", font=("Segoe UI", 12, "bold"))
task_label.pack(pady=5)

task_entry = ttkb.Entry(main_frame, font=("Segoe UI", 12))
task_entry.pack(pady=5)

add_task_button = ttkb.Button(main_frame, text="✚ Add task", command=lambda: add_task(task_entry, task_combobox, is_billable, update_status), bootstyle="success")
add_task_button.pack(pady=5)

delete_task_button = ttkb.Button(main_frame, text="❌ Delete selected task", command=lambda: delete_task(task_combobox, update_status), bootstyle="danger")
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

# Rappel d'inactivité si activé
def check_for_inactivity():
    if work_button['state'] == ttkb.NORMAL and app_settings.get("reminder_enabled", True):
        send_push_notification("Flowmodoro", "N'oubliez pas de démarrer une session !", app_settings)
    root.after(600000, check_for_inactivity)  # 10 minutes

check_for_inactivity()


# Clean up menu bar process and timer file when GUI is closed
def on_app_close():
    """Clean up menu bar process and timer file when GUI is closed."""
    global menu_bar_process
    if menu_bar_process:
        menu_bar_process.terminate()
        menu_bar_process = None
    if TIMER_FILE.exists():
        TIMER_FILE.unlink()
    if BREAK_FILE.exists():
        BREAK_FILE.unlink()
    root.destroy()


if __name__ == "__main__":
    if "--menu-bar" in sys.argv:
        FlowModoroBar().run()
    else:
        if sys.platform == "darwin":
            menu_bar_process = subprocess.Popen([sys.executable, __file__, "--menu-bar"])
        # When the user closes the main window, clean up the menu bar process
        root.protocol("WM_DELETE_WINDOW", on_app_close)
        root.mainloop()