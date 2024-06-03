#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import time
import threading
import pygame

#Initialize pygame mixer for playing sounds
pygame.mixer.init()

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def start_work_session():
    global start_time
    start_time = time.time()
    work_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    update_timer()

def stop_work_session():
    global end_time, work_duration
    end_time = time.time()
    work_duration = end_time - start_time
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

root = tk.Tk()
root.title("FlowModoro")

timer_label = tk.Label(root, text="00:00", font=("Helvetica", 48))
timer_label.pack(pady=20)

work_button = tk.Button(root, text="Start Work Session", command=start_work_session)
work_button.pack(side=tk.LEFT, padx=20)

stop_button = tk.Button(root, text="Stop Work Session", command=stop_work_session, state=tk.DISABLED)
stop_button.pack(side=tk.RIGHT, padx=20)

root.mainloop()


