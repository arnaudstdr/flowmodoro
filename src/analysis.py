import json
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
from tkinter import scrolledtext, filedialog, messagebox
import ttkbootstrap as ttkb
import csv  # Ajouter l'importation du module csv
from src.config import session_file
from src.sessions import load_sessions

def analyze_time_by_task_and_category(root):
    sessions = load_sessions()
    analysis_data = defaultdict(lambda: defaultdict(lambda: {"time": 0, "billable": 0}))

    for session in sessions:
        category = session["category"]
        task = session["task"]
        duration = session["duration"]
        billable = session.get("billable", False)

        analysis_data[category][task]["time"] += duration
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

def export_analysis_to_csv(root):
    sessions = load_sessions()
    analysis_data = defaultdict(lambda: defaultdict(lambda: {"time": 0, "billable": 0}))

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

def show_history(root):
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

def show_weekly_analysis(root):
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

def show_category_analysis_graph(root):
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