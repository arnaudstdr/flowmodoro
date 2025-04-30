import ttkbootstrap as ttkb
from tkinter import messagebox, scrolledtext, filedialog
from src.config import app_settings
from src.utils import save_settings

def open_settings_window(root):
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