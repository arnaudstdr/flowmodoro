#!/usr/bin/env python3

import time

def start_work_session():
    start_time = time.time()
    input("Press Enter to stop the work session ...")
    end_time = time.time()
    work_duration = end_time - start_time
    return work_duration

def start_timer(seconds):
    while seconds > 0:
        minutes,seconds_remaining = divmod(int(seconds), 60)
        print(f"{minutes:02d}:{seconds_remaining:02d}", end="\r")
        time.sleep(1)
        seconds -= 1
    print("Time's up !")

def main():
    while True:
        print("Work session started.")
        work_duration = start_work_session()
        work_minutes = work_duration / 60
        print(f"Work session ended. Duration : {work_minutes:.2F} minutes.")

        break_duration = work_duration / 5
        break_minutes = break_duration / 60
        print(f"Break time : {break_minutes:.2f} minutes.")

        start_timer(break_duration)

        user_imput = input("Start another session ? (y/n) ")
        if user_imput.lower() != 'y':
            break

if __name__ == "__main__":
    main()

