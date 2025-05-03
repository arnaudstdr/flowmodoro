#!/usr/bin/env python3

import sys
import time
import rumps
from pathlib import Path

TIMER_FILE = Path.home() / ".flowmodoro_timer"
BREAK_FILE = Path.home() / ".flowmodoro_break_timer"

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

if __name__ == "__main__":
    FlowModoroBar().run()