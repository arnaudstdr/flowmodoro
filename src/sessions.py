import json
from datetime import datetime
from collections import defaultdict
from src.config import session_file

def load_sessions():
    try:
        with open(session_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_session(start_time, end_time, duration, category, task, is_billable):
    start_datetime = datetime.fromtimestamp(start_time)
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