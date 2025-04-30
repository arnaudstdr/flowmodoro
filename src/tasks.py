import json
from src.config import task_file
from tkinter import messagebox
import ttkbootstrap as ttkb 

def load_tasks():
    try:
        with open(task_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def get_task_names():
    tasks = load_tasks()
    return sorted([task["name"] for task in tasks])

def save_task(task, is_billable):
    tasks = load_tasks()
    billable = is_billable.get()
    task_data = {"name": task, "billable": billable}
    if task_data not in tasks:
        tasks.append(task_data)
        with open(task_file, "w") as file:
            json.dump(tasks, file, indent=2)

    # Réinitialiser la case à cocher après ajout
    is_billable.set(False)

def add_task(task_entry, task_combobox, is_billable, update_status):
    task = task_entry.get()
    if task:
        save_task(task, is_billable)
        task_combobox['values'] = get_task_names()
        task_entry.delete(0, ttkb.END)
        update_status(f"Tâche '{task}' ajoutée.")
    else:
        update_status("Erreur : entrez une tâche avant d'ajouter.")

def delete_task(task_combobox, update_status):
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