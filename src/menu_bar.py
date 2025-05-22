#!/usr/bin/env python3

import sys
import time
import rumps
from pathlib import Path

TIMER_FILE = Path.home() / ".flowmodoro_timer"
BREAK_FILE = Path.home() / ".flowmodoro_break_timer"

def format_timer_display(total_seconds):
    if total_seconds >= 3600:
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"
    else:
        minutes, seconds = divmod(int(total_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

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
                self.title = format_timer_display(remaining)
            else:
                BREAK_FILE.unlink()
                self.title = "00:00"
        # Otherwise if work session active, show elapsed
        elif TIMER_FILE.exists():
            start_ts = float(TIMER_FILE.read_text())
            elapsed = time.time() - start_ts
            self.title = format_timer_display(elapsed)
        else:
            self.title = "00:00"

if __name__ == "__main__":
    FlowModoroBar().run()