import sqlite3
import json


def init_db():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            user_email TEXT NOT NULL,
            item_type TEXT NOT NULL,
            details TEXT NOT NULL,
            FOREIGN KEY(user_email) REFERENCES users(email) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    return conn, c


def login(conn, c):
    email = input("Please enter your email to log in: ")
    password = input("Please enter your password: ")
    c.execute("SELECT first_name, password FROM users WHERE email = ?", (email,))
    user_info = c.fetchone()

    if user_info:
        first_name, stored_password = user_info
        if stored_password is None:
            print("Welcome back! Please set a new password for your account.")
            new_password = input("Enter a new password: ")
            c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            print("Password updated successfully!")
            return email
        elif stored_password == password:
            print(f"Welcome, {first_name}!")
            return email
        else:
            print("Incorrect password.")
            return None
    else:
        print("User email not found.")
        return None


def signup(conn, c):
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    email = input("Enter your email: ")
    password = input("Create a password: ")
    try:
        c.execute("INSERT INTO users (email, first_name, last_name, password) VALUES (?, ?, ?, ?)",
                  (email, first_name, last_name, password))
        conn.commit()
        print(f"Account created successfully! Your new user email is {email}.")
        return email
    except sqlite3.IntegrityError:
        print("An account with that email already exists.")
        return None


def add_item(conn, c, current_user_email):
    item_type = input("Enter the type of item (e.g., 'book', 'task', 'car'): ")
    details = {}
    print("Enter key-value pairs for the item details (type 'done' when finished):")
    while True:
        key = input("Key: ")
        if key.lower() == 'done':
            break
        value = input(f"Value for '{key}': ")
        details[key] = value

    if details:
        details_json = json.dumps(details)
        try:
            c.execute("INSERT INTO items (user_email, item_type, details) VALUES (?, ?, ?)",
                      (current_user_email, item_type, details_json))
            conn.commit()
            print(f"Item of type '{item_type}' added successfully.")
        except sqlite3.IntegrityError as e:
            print(f"An error occurred: {e}")
    else:
        print("No details entered. Item not added.")


def view_items(c, current_user_email):
    print("--- Your Items ---")
    c.execute("SELECT id, item_type, details FROM items WHERE user_email = ?", (current_user_email,))
    items = c.fetchall()
    if not items:
        print("You have no items in the database.")
        return

    for item in items:
        item_id, item_type, details_json = item
        details = json.loads(details_json)
        print("-" * 40)
        print(f"ID: {item_id}")
        print(f"Type: {item_type}")
        print("Details:")
        for key, value in details.items():
            print(f"  - {key}: {value}")


def view_users(c):
    print("--- All Users ---")
    print("-" * 50)
    print(f"{'Email':<30} | {'First Name':<15} | {'Last Name':<15}")
    print("-" * 50)
    c.execute("SELECT email, first_name, last_name FROM users")
    users = c.fetchall()
    for user in users:
        print(f"{user[0]:<30} | {user[1]:<15} | {user[2]:<15}")
    if not users:
        print("No users found.")


def delete_item(conn, c, current_user_email):
    view_items(c, current_user_email)
    try:
        item_id = int(input("\nEnter what item you would like to delete (ID): "))
        c.execute("SELECT id FROM items WHERE id = ? AND user_email = ?", (item_id, current_user_email))
        if c.fetchone():
            decision = input(f"Are you sure you want to delete item with ID {item_id}? (y/n): ")
            if decision.lower() == 'y':
                c.execute("DELETE FROM items WHERE id = ?", (item_id,))
                conn.commit()
                print("Item deleted successfully!")
            else:
                print("Deletion cancelled.")
        else:
            print("Invalid item ID or you do not have permission to delete this item.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def main():
    conn, c = init_db()
    current_user_email = None

    print("Welcome to the interactive database client!")

    while True:
        if not current_user_email:
            print("\n--- Choose an option ---")
            print("1. Log in")
            print("2. Sign up")
            print("3. Exit")
            choice = input("Enter your choice (1-3): ")

            if choice == '1':
                current_user_email = login(conn, c)
            elif choice == '2':
                current_user_email = signup(conn, c)
            elif choice == '3':
                print("Exiting...")
                conn.close()
                break
            else:
                print("Invalid choice. Please try again.")
                continue

        if current_user_email:
            print("\n--- Main Menu ---")
            print("1. Add a new item")
            print("2. View your items")
            print("3. View all users")
            print("4. Delete items")
            print("5. Log out")
            print("6. Exit")
            command = input("Enter your choice (1-6): ")

            if command == '1':
                add_item(conn, c, current_user_email)
            elif command == '2':
                view_items(c, current_user_email)
            elif command == '3':
                view_users(c)
            elif command == '4':
                delete_item(conn, c, current_user_email)
            elif command == '5':
                print("Logging out...")
                current_user_email = None
            elif command == '6':
                print("Exiting...")
                conn.close()
                break
            else:
                print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()
