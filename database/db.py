import sqlite3
from flask import g, current_app
from werkzeug.security import generate_password_hash

def get_db():
    """
    Returns the database connection for the current request.
    If no connection exists, it creates one, enables foreign keys,
    and sets the row_factory to sqlite3.Row.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.execute("PRAGMA foreign_keys = ON;")
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    """
    Initializes the database by creating the users and expenses tables.
    Safe to call multiple times.
    """
    with sqlite3.connect(current_app.config['DATABASE']) as conn:
        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')

        # Create expenses table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()

def seed_db():
    """
    Seeds the database with a demo user and sample expenses.
    Prevents duplicate seeding by checking for existing users.
    """
    with sqlite3.connect(current_app.config['DATABASE']) as conn:
        # Prevent duplicate seeding
        cursor = conn.execute("SELECT count(*) FROM users")
        if cursor.fetchone()[0] > 0:
            return

        # 1. Insert Demo User
        demo_user_password = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", demo_user_password)
        )
        user_id = cursor.lastrowid

        # 2. Insert 8 sample expenses across all categories
        # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        expenses = [
            (user_id, 12.50, 'Food', '2026-10-01', 'Lunch at Cafe'),
            (user_id, 45.00, 'Transport', '2026-10-02', 'Weekly Fuel'),
            (user_id, 120.00, 'Bills', '2026-10-03', 'Internet Bill'),
            (user_id, 30.00, 'Health', '2026-10-05', 'Pharmacy'),
            (user_id, 15.00, 'Entertainment', '2026-10-07', 'Movie Ticket'),
            (user_id, 65.20, 'Shopping', '2026-10-10', 'New Shirt'),
            (user_id, 10.00, 'Other', '2026-10-12', 'Parking Fee'),
            (user_id, 22.00, 'Food', '2026-10-15', 'Dinner'),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )

        conn.commit()
