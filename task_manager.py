from datetime import datetime
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("CODE VERSION 999")

logged_in_user = None


# -- Helper functions --
print("A")
def load_users():
    users = {}

    if not os.path.exists("user.txt"):
        print("No user file found. Creating admin account.")

        username = input("Create admin username: ")
        password = input("Create admin password: ")

        users[username] = password

        with open("user.txt", "w") as file:
            file.write(f"{username}, {password}\n")

        return users

    with open("user.txt", "r") as file:
        for line in file:
            line = line.strip()

            if line == "":
                continue

            username, password = line.split(", ")
            users[username] = password

    return users


def load_tasks():
    tasks = []

    try:
        with open("tasks.txt", "r") as file:
            for line in file:
                line = line.strip()

                if line == "":
                    continue

                task_data = line.split(", ")

                if len(task_data) == 6:
                    tasks.append(task_data)

    except FileNotFoundError:
        with open("tasks.txt", "w") as file:
            pass

    return tasks


def save_tasks(tasks):
    with open("tasks.txt", "w") as file:
        for i, task in enumerate(tasks):
            file.write(", ".join(task))

            if i != len(tasks) - 1:
                file.write("\n")


# Add one line to a file
def append_line(filename, text):
    with open(filename, "a+") as file:
        file.seek(0)
        content = file.read()

        if content != "" and not content.endswith("\n"):
            file.write("\n")

        file.write(text)


# Turn a date string into a real date
def string_to_date(date_string):
    try:
        return datetime.strptime(date_string, "%d %b %Y")
    except ValueError:
        return None


# Keep asking until the date is correct
def get_valid_date(prompt, allow_blank=False):
    while True:
        date_input = input(prompt)

        if allow_blank and date_input == "":
            return ""

        if string_to_date(date_input) is not None:
            return date_input

        print("Invalid date. Use this format: 25 Oct 2019")


def is_task_overdue(task):
    due_date = string_to_date(task[4])

    if due_date is None:
        return False

    return task[5] == "No" and due_date.date() < datetime.today().date()


# Show one task nicely
def display_task(task, task_number=None):
    print("\n" + "-" * 50)

    if task_number is not None:
        print(f"Task number:    {task_number}")

    print(f"Task:           {task[1]}")
    print(f"Assigned to:    {task[0]}")
    print(f"Date assigned:  {task[3]}")
    print(f"Due date:       {task[4]}")
    print(f"Completed:      {task[5]}")
    print("Description:")
    print(task[2])

    print("-" * 50)


# Check if the task number entered is valid
def get_task_choice(amount, prompt):
    while True:
        choice = input(prompt)

        if choice == "-1":
            return -1

        if not choice.isdigit():
            print("Please enter a valid task number.")
            continue

        choice = int(choice)

        if choice < 1 or choice > amount:
            print("That task number does not exist.")
            continue

        return choice


# -- Required functions --

def reg_user():
    global users

    if logged_in_user != admin_user:
        print("Only admin can register users.")
        return

    while True:
        new_username = input("Enter a new username: ")

        if new_username == "":
            print("Username cannot be empty.")
            continue

        if new_username in users:
            print("That username already exists.")
            continue

        new_password = input("Enter a new password: ")
        confirm_password = input("Confirm the password: ")

        if new_password != confirm_password:
            print("Passwords do not match.")
            continue

        append_line("user.txt", f"{new_username}, {new_password}")
        users[new_username] = new_password

        print("New user added successfully.")
        return


def add_task():
    while True:
        task_username = input("Enter the username of the person the task "
                              "is assigned to: ")

        if task_username not in users:
            print("That user does not exist.")
            continue

        break

    task_title = input("Enter the title of the task: ")
    task_description = input("Enter the description of the task: ")
    task_due_date = get_valid_date("Enter the due date of the task "
                                   "(e.g. 25 Oct 2019): ")
    current_date = datetime.now().strftime("%d %b %Y")

    append_line(
        "tasks.txt",
        f"{task_username}, {task_title}, {task_description}, {current_date}, "
        f"{task_due_date}, No"
    )

    print("Task added successfully.")


def view_all():
    tasks = load_tasks()

    if len(tasks) == 0:
        print("There are no tasks in the file.")
        return

    for task in tasks:
        display_task(task)


def view_mine():
    tasks = load_tasks()
    my_task_indexes = []

    # Find only this user's tasks
    for i, task in enumerate(tasks):
        if task[0] == logged_in_user:
            my_task_indexes.append(i)
            display_task(task, len(my_task_indexes))

    if len(my_task_indexes) == 0:
        print("You have no tasks assigned to you.")
        return

    choice = get_task_choice(
        len(my_task_indexes),
        "Enter a task number to select a task, or -1 "
        "to return to the main menu: "
    )

    if choice == -1:
        return

    selected_index = my_task_indexes[choice - 1]
    selected_task = tasks[selected_index]

    display_task(selected_task, choice)

    while True:
        action = input("Enter 'c' to mark complete, 'e' to edit, or '-1' "
                       "to return: ").lower()

        if action == "-1":
            return

        elif action == "c":
            if selected_task[5] == "Yes":
                print("This task is already completed.")
            else:
                selected_task[5] = "Yes"
                save_tasks(tasks)
                print("Task marked as completed.")
            return

        elif action == "e":
            if selected_task[5] == "Yes":
                print("Completed tasks cannot be edited.")
                return

            # Change username only if a valid one is entered
            while True:
                new_username = input("Enter a new username or press Enter "
                                     "to keep the current username: ")

                if new_username == "":
                    break

                if new_username not in users:
                    print("That user does not exist.")
                    continue

                selected_task[0] = new_username
                break

            new_due_date = get_valid_date(
                "Enter a new due date or press Enter to keep the current "
                "due date (e.g. 25 Oct 2019): ",
                True
            )

            if new_due_date != "":
                selected_task[4] = new_due_date

            save_tasks(tasks)
            print("Task updated successfully.")
            return

        else:
            print("Invalid option. Please try again.")


def view_completed():
    tasks = load_tasks()
    found_completed = False

    for i, task in enumerate(tasks, start=1):
        if task[5] == "Yes":
            display_task(task, i)
            found_completed = True

    if not found_completed:
        print("There are no completed tasks.")


def delete_task():
    if logged_in_user != admin_user:
        print("Only admin can delete tasks.")
        return

    tasks = load_tasks()

    if len(tasks) == 0:
        print("There are no tasks to delete.")
        return

    for i, task in enumerate(tasks, start=1):
        display_task(task, i)

    choice = get_task_choice(
        len(tasks),
        "Enter the task number to delete, or -1 to return to the main menu: "
    )

    if choice == -1:
        return

    confirm = input("Are you sure you want to delete this task? "
                    "(y/n): ").lower()

    if confirm == "y":
        del tasks[choice - 1]
        save_tasks(tasks)
        print("Task deleted successfully.")
    else:
        print("Task was not deleted.")


def generate_reports():
    all_users = load_users()
    all_tasks = load_tasks()

    total_users = len(all_users)
    total_tasks = len(all_tasks)
    completed_tasks = 0
    uncompleted_tasks = 0
    overdue_tasks = 0

    # Count task types
    for task in all_tasks:
        if task[5] == "Yes":
            completed_tasks += 1
        else:
            uncompleted_tasks += 1

        if is_task_overdue(task):
            overdue_tasks += 1

    if total_tasks == 0:
        incomplete_percentage = 0
        overdue_percentage = 0
    else:
        incomplete_percentage = (uncompleted_tasks / total_tasks) * 100
        overdue_percentage = (overdue_tasks / total_tasks) * 100

    with open("task_overview.txt", "w") as file:
        file.write(f"Total tasks: {total_tasks}\n")
        file.write(f"Completed tasks: {completed_tasks}\n")
        file.write(f"Uncompleted tasks: {uncompleted_tasks}\n")
        file.write(f"Overdue tasks: {overdue_tasks}\n")
        file.write(f"Percentage incomplete: {incomplete_percentage:.2f}%\n")
        file.write(f"Percentage overdue: {overdue_percentage:.2f}%\n")

    with open("user_overview.txt", "w") as file:
        file.write(f"Total users: {total_users}\n")
        file.write(f"Total tasks: {total_tasks}\n\n")

        for username in all_users:
            user_task_total = 0
            user_completed = 0
            user_uncompleted = 0
            user_overdue = 0

            for task in all_tasks:
                if task[0] == username:
                    user_task_total += 1

                    if task[5] == "Yes":
                        user_completed += 1
                    else:
                        user_uncompleted += 1

                    if is_task_overdue(task):
                        user_overdue += 1

            if total_tasks == 0:
                percentage_of_total = 0
            else:
                percentage_of_total = (user_task_total / total_tasks) * 100

            if user_task_total == 0:
                percentage_completed = 0
                percentage_uncompleted = 0
                percentage_overdue = 0
            else:
                percentage_completed = (user_completed / user_task_total) * 100
                percentage_uncompleted = (user_uncompleted /
                                          user_task_total) * 100
                percentage_overdue = (user_overdue / user_task_total) * 100

            file.write(f"User: {username}\n")
            file.write(f"Tasks assigned: {user_task_total}\n")
            file.write(f"Percentage of total tasks assigned: "
                       f"{percentage_of_total:.2f}%\n")
            file.write(f"Percentage of tasks completed: "
                       f"{percentage_completed:.2f}%\n")
            file.write(f"Percentage of tasks still to complete: "
                       f"{percentage_uncompleted:.2f}%\n")
            file.write(f"Percentage of tasks overdue: "
                       f"{percentage_overdue:.2f}%\n\n")

    print("Reports generated successfully.")


def display_statistics():
    # Make the report files first if they do not exist
    if not os.path.exists("task_overview.txt") or not os.path.exists(
                          "user_overview.txt"):
        generate_reports()

    print("\n" + "=" * 50)
    print("TASK OVERVIEW")
    print("=" * 50)

    with open("task_overview.txt", "r") as file:
        print(file.read())

    print("\n" + "=" * 50)
    print("USER OVERVIEW")
    print("=" * 50)

    with open("user_overview.txt", "r") as file:
        print(file.read())


# -- Login --

users = load_users()
admin_user = list(users.keys())[0]

while True:
    username = input("Username: ")
    password = input("Password: ")

    if username not in users:
        print("That username does not exist. Please try again.")
        continue

    if users[username] != password:
        print("Incorrect password. Please try again.")
        continue

    logged_in_user = username
    print("Login successful.")
    break


# -- Main menu --

while True:
    if logged_in_user != admin_user:
        menu = input(
            '''Select one of the following options:
r - register a user
a - add task
va - view all tasks
vm - view my tasks
vc - view completed tasks
del - delete a task
ds - display statistics
gr - generate reports
e - exit
: '''
        ).lower()
    else:
        menu = input(
            '''Select one of the following options:
a - add task
va - view all tasks
vm - view my tasks
e - exit
: '''
        ).lower()

    if menu == "r" and logged_in_user == admin_user:
        reg_user()

    elif menu == "a":
        add_task()

    elif menu == "va":
        view_all()

    elif menu == "vm":
        view_mine()

    elif menu == "vc" and logged_in_user == admin_user:
        view_completed()

    elif menu == "del" and logged_in_user == admin_user:
        delete_task()

    elif menu == "gr" and logged_in_user == admin_user:
        generate_reports()

    elif menu == "ds" and logged_in_user == admin_user:
        display_statistics()

    elif menu == "e":
        print("Goodbye!!!")
        break

    else:
        print("You have entered an invalid input. Please try again.")
