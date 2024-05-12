import hashlib
import sqlite3
from datetime import datetime
import os
import getpass  # For user authentication
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Initialize GUI for file selection and user feedback
root = tk.Tk()
root.withdraw()  # Hide the main window

# User Authentication
def user_authentication():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    # Implement database check or other authentication mechanism here
    # Placeholder logic
    if username == "sayed" and password == "forensikguy":
        messagebox.showinfo("Authentication", "Authentication Successful!")
        return True
    else:
        messagebox.showerror("Authentication", "Authentication Failed!")
        return False

# Initialize database with error handling
def init_db():
    try:
        conn = sqlite3.connect('cochain.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_changes (
                id INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL,
                action TEXT NOT NULL,
                hash TEXT NOT NULL,
                user TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Generate SHA-256 hash value for a given file path
def generate_hash(file_path):
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            buf = file.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        messagebox.showerror("Hashing Error", f"An error occurred while generating hash for {file_path}: {e}")
        return None

# Log changes to both database and a text file
def log_changes(file_paths, action, user):
    for file_path in file_paths:
        hash_value = generate_hash(file_path)
        if hash_value:
            try:
                # Log to database
                conn = sqlite3.connect('cochain.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO file_changes (file_path, action, hash, user)
                    VALUES (?, ?, ?, ?)
                ''', (file_path, action, hash_value, user))
                conn.commit()
                # Log to text file
                with open('change_log.txt', 'a') as log_file:
                    log_file.write(f"{datetime.now()}: {action} performed on {file_path} by {user}, Hash: {hash_value}\n")
            except sqlite3.Error as e:
                messagebox.showerror("Logging Error", f"An error occurred while logging changes: {e}")
            finally:
                conn.close()

# Verify the integrity of files
def verify_integrity(file_path):
    try:
        current_hash = generate_hash(file_path)
        conn = sqlite3.connect('cochain.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT hash FROM file_changes
            WHERE file_path = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (file_path,))
        row = cursor.fetchone()
        if row and row[0] == current_hash:
            messagebox.showinfo("Integrity Check", "The integrity of the file is intact.")
        else:
            messagebox.showwarning("Integrity Check", "Warning: The integrity of the file might be compromised.")
    except sqlite3.Error as e:
        messagebox.showerror("Integrity Verification Error", f"An error occurred during integrity verification: {e}")
    finally:
        conn.close()

# Main function to orchestrate the CoC process
if __name__ == '__main__':
    if user_authentication():
        init_db()
        file_paths = filedialog.askopenfilenames(title="Select files to monitor")  # File selection dialog
        user = 'forensic_user'  # Replace with actual user from authentication
        log_changes(file_paths, 'Creation', user)
        for file_path in file_paths:
            verify_integrity(file_path)
