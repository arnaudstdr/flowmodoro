#!/usr/bin/env python3

import time

def start_timer(minutes):
    total_seconds = minutes * 60
    while total_seconds > 0:
        minutes, seconds = divmod(total_seconds, 60)
        print(f"{minutes:02d}:{seconds:02d}", end="\r")
        time.sleep(1)
        total_seconds -= 1
    print("Time's UP !")

def work_session(duration):
    print("Work session started")
    start_timer(duration)
    print("Work session ended")

def short_break(duration):
    print("Short break started")
    start_timer(duration)
    print("Short break ended")

def long_break(duration):
    print("Long break started")
    start_timer(duration)
    print("Long break ended")

def main():
    work_duration = 1  # 25 minutes
    short_break_duration = 1  # 5 minutes
    long_break_duration = 15  # 15 minutes
    session_before_long_break = 4

    session_count = 0

    while True :
        work_session(work_duration)
        session_count += 1

        if session_count % session_before_long_break == 0:
            long_break(long_break_duration)
        else:
            short_break(short_break_duration)

        user_input = input("Strat another session ? (y/n) : ")
        if user_input.lower() != 'y':
            break

if __name__ == "__main__":
    main()