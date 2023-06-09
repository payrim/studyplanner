import json
import re
from datetime import datetime, timedelta
import os
from clearterminal import clear_terminal

LECTURES_FILE = "lectures.json"

def init():
    try:
        with open('lectures.json', 'r') as f:
            lectures = json.load(f)
            for d in lectures:
                d["deadline"] = datetime.strptime(d["deadline"], "%Y-%m-%d").date()
            update_index(lectures)
            return lectures
    except FileNotFoundError:
        return []



def save(lectures):
    clear_terminal()
    with open('lectures.json', 'w') as f:
        lectures_copy = lectures.copy()
        for lec in lectures_copy:
            if isinstance(lec['deadline'], datetime):
                lec['deadline'] = lec['deadline'].strftime('%d-%m-%Y')
        json.dump(lectures_copy, f, indent=4, default=str)

def add_lecture(lectures):
    clear_terminal()
    name = input("\nEnter video name: ")
    duration_str = input("Enter video duration (HH:MM): ")
    duration_hour, duration_minute = map(int, duration_str.split(":"))
    duration = duration_hour * 60 + duration_minute
    
    # check if the input contains a '+n' format
    deadline_input = input("Enter deadline (DD-MM-YYYY or +n): ")
    if re.match(r'\+\d+', deadline_input):
        days_from_now = int(deadline_input[1:])
        deadline = datetime.now().date() + timedelta(days=days_from_now)
    else:
        deadline = datetime.strptime(deadline_input, "%d-%m-%Y").date()
    
    lectures.append({
        "name": name,
        "duration": duration,
        "amount_watched": 0,
        "deadline": deadline,
        "amount_done": 0,
        "active_status": 1
    })
    lectures.sort(key=lambda x: x["deadline"])
    update_index(lectures)
    save(lectures)

def update_index(lectures):
    for i, lecture in enumerate(lectures):
        lecture["index"] = i + 1


def edit_notes():
    if os.name == 'nt':
        notes_file = "C:\\Program Files\\Planner\\video.txt"
        editor = 'notepad'
    else:
        notes_file = os.path.expanduser("~/plannerconf/videonote.txt")
        editor = 'vim'
    os.system(f"{editor} {notes_file}")

def flush_database(lectures):
    clear_terminal()
    confirm = input("Are you sure you want to flush the database? This action cannot be undone. (y/n): ")
    if confirm.lower() == 'y':
        lectures.clear()
        save(lectures)
        print("All lectures removed from the database.")
    else:
        print("Database flush cancelled.")


def show_lectures(lectures):
    clear_terminal()
    print("\n\nIndex\tName\t\t\tTime left\tDeadline")
    total_amount = sum(lecture["duration"] for lecture in lectures if lecture["active_status"] == 1)
    total_amount_watched = sum(lecture["amount_watched"] for lecture in lectures if lecture["active_status"] == 1)
    progress_bar_length = 20
    progress_bar_fill = '█'
    
    for i, lecture in enumerate(lectures):
        if lecture["active_status"] == 1:
            time_left = lecture["duration"] - lecture["amount_watched"]
            time_left_str = f"{time_left // 60:02d}:{time_left % 60:02d}"  # format the time_left as HH:MM
            deadline = lecture["deadline"].strftime("%d-%m-%Y")
            print(f"{i+1}\t{lecture['name']}\t\t{time_left_str}\t\t{deadline}")
    
    progress_bar_fill_count = int(total_amount_watched / total_amount * progress_bar_length)
    progress_bar = f"[{progress_bar_fill * progress_bar_fill_count}{' ' * (progress_bar_length - progress_bar_fill_count)}]"
    print(f"\nProgress: {progress_bar} {int(total_amount_watched / total_amount * 100)}%")


def modify_lecture(lectures):
    clear_terminal()
    print("\n\nSelect lecture to modify:\n")
    for lecture in lectures:
        if lecture["active_status"] == 1:
            print(f"{lecture['index']}. {lecture['name']}\t\tT: {lecture['duration']-lecture['amount_watched']}")
    lecture_index = int(input("\nEnter lecture index: ")) - 1
    amount_watched = int(input("Enter amount watched: "))
    lectures[lecture_index]["amount_watched"] += amount_watched
    save(lectures)


def change_deadline(lectures):
    clear_terminal()
    print("\n\nSelect lecture to change the deadline:\n")
    for lecture in lectures:
        if lecture["active_status"] == 1:
            print(f"{lecture['index']}. {lecture['name']}\t\tT: {lecture['duration']-lecture['amount_watched']}")
    lecture_index = int(input("\nEnter lecture index: ")) - 1
    
    if lecture_index < 0 or lecture_index >= len(lectures):
        print("Invalid lecture index")
        return
    
    days = int(input("Enter the number of days to add or subtract from the deadline: "))
    lecture = lectures[lecture_index]
    current_deadline = lecture["deadline"]
    new_deadline = current_deadline + timedelta(days=days)
    lecture["deadline"] = new_deadline
    save(lectures)
    print(f"Deadline for {lecture['name']} changed from {current_deadline} to {new_deadline}")


def remove_lecture(lectures):
    clear_terminal()
    for lecture in lectures:
        if lecture["active_status"] == 1:
            print(f"\n{lecture['index']}. {lecture['name']}\t\tT: {lecture['duration']-lecture['amount_watched']}")
    index = input("\nEnter the index of the lecture you want to remove: ")
    for lecture in lectures:
        if lecture['index'] == int(index) and lecture["active_status"] == 1:
            lectures.remove(lecture)
            print(f"Lecture with index {index} removed successfully.")
            save(lectures)
            break
    else:
        print(f"No lecture found with index {index}.")

def daily_workload(lectures):
    clear_terminal()
    today = datetime.now().date()
    total_workload_minutes = 0

    print("\n\nVideo\t\tTime left\tDays left\tDaily workload\tWatched (%)")
    print("---------------------------------------------------------------------------")
    
    for lecture in lectures:
        if lecture["active_status"] == 1:
            time_left = lecture["duration"] - lecture["amount_watched"]
            time_left_str = f"{time_left // 60:02d}:{time_left % 60:02d}"
            days_left = (lecture["deadline"] - today).days
            
            if days_left < 1:
                print(
                    f"{lecture['name']}\t\t{time_left_str}\t\t- \t\tOverdue!\t{int(lecture['amount_watched'] / lecture['duration'] * 100)}%"
                )
            else:
                daily_workload = int(time_left / days_left)
                daily_workload_str = f"{daily_workload // 60:02d}:{daily_workload % 60:02d}"
                print(
                    f"{lecture['name']}\t{time_left_str}\t\t{days_left}\t\t{daily_workload_str}\t\t{int(lecture['amount_watched'] / lecture['duration'] * 100)}%"
                )
                total_workload_minutes += daily_workload
    
    total_workload_hours = total_workload_minutes // 60
    total_workload_minutes %= 60
    total_workload_str = f"{total_workload_hours:02d}:{total_workload_minutes:02d}"
    
    print("---------------------------------------------------------------------------")
    print(f"Daily estimate: {total_workload_str}")




def hibernate_lecture(lectures):
    clear_terminal()
    print("\n\nSelect lecture to hibernate or activate:\n")
    for lecture in lectures:
        status = "Hibernated" if lecture["active_status"] == 0 else "Active"
        print(f"{lecture['index']}.\t {lecture['name']}\t\tStatus: {status}")
    lecture_index = int(input("\nEnter lecture index: ")) - 1
    
    if lecture_index < 0 or lecture_index >= len(lectures):
        print("Invalid lecture index")
        return
    
    lecture = lectures[lecture_index]
    lecture["active_status"] = 0 if lecture["active_status"] == 1 else 1
    status = "Hibernated" if lecture["active_status"] == 0 else "Active"
    save(lectures)
    print(f"Lecture '{lecture['name']}' is now {status}")

def main():
    clear_terminal()
    lectures = init()
    while True:
        print("\n ||lecture videos||\n\n")
        print("a. Add lecture")
        print("l. Load lectures")
        print("v. Save lectures")
        print("s. Show lectures")
        print("d. Daily workload")
        print("m. Modify lecture")
        print("c. Change deadline")
        print("h. Hibernate a lecture")
        print("r. Remove a lecture")
        print("n. Lecture notes")
        print("f. Flush database")
        print("q. Exit")
        choice = input("\nEnter your choice: ")
        if choice == "a":
            add_lecture(lectures)
        elif choice == "l":
            lectures = init()
            clear_terminal()
        elif choice == "v":
            save(lectures)
        elif choice == "s":
            show_lectures(lectures)
            input("\n\nPress any key to continue.....")
            clear_terminal()
        elif choice == "d":
            daily_workload(lectures)
            input("\n\nPress any key to continue.....")
            clear_terminal()
        elif choice == "m":
            modify_lecture(lectures)
        elif choice == "r":
            remove_lecture(lectures)
        elif choice == "c":
            change_deadline(lectures)
        elif choice == "h":
            clear_terminal()
            hibernate_lecture(lectures)
        elif choice == "n":
            edit_notes()
            clear_terminal()
        elif choice == "f":
            flush_database(lectures)
        elif choice == "q":
            break
        else:
            clear_terminal()
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
