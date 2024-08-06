#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import threading
import pygame
import json
from datetime import datetime

#Initialize pygame mixer for playing sounds
pygame.mixer.init()

# Global variables
current_session_counter = 0
session_file = "sessions.json"

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

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
    save_session(start_time, end_time, work_duration)
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
        messagebox.showinfo("Time's up", "Time's up")

    timer_thread = threading.Thread(target=countdown)
    timer_thread.start()

def save_session(start_time, end_time, duration):
    session_data = {
        "start_time": datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'),
        "duration": duration
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
    history_window.title("Session History")

    text_area = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    for session in sessions:
        session_info = f"Start: {session['start_time']}, End: {session['end_time']}, Duration: {session['duration'] / 60:.2f} minutes\n"
        text_area.insert(tk.END, session_info)

    text_area.config(state=tk.DISABLED)

def update_session_count():
    session_count_label.config(text=f"Current Sessions: {current_session_counter}")

root = tk.Tk()
root.title("FlowModoro")

timer_label = tk.Label(root, text="00:00", font=("Helvetica", 48))
timer_label.pack(pady=20)

session_count_label = tk.Label(root, text=f"Current Session: {current_session_counter}", font=("Helvetica", 16))
session_count_label.pack(pady=10)

work_button = tk.Button(root, text="Start Work Session", command=start_work_session)
work_button.pack(side=tk.LEFT, padx=20)

stop_button = tk.Button(root, text="Stop Work Session", command=stop_work_session, state=tk.DISABLED)
stop_button.pack(side=tk.RIGHT, padx=20)

history_button = tk.Button(root, text="View History", command=show_history)
history_button.pack(pady=20)

root.mainloop()


