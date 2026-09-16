import sqlite3
import os

def build_schema():
    # 1. Set up the connection and path
    db_path = os.path.join(os.path.dirname(__file__), 'palworld.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Turn on Foreign Key constraints (SQLite has this off by default)
    cursor.execute('PRAGMA foreign_keys = ON;')

    # 3. Create the Base Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL
    )
    ''')

    # 4. Create the Recipes Table (Links items to items)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crafted_item_id INTEGER,
        ingredient_item_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY(crafted_item_id) REFERENCES items(id),
        FOREIGN KEY(ingredient_item_id) REFERENCES items(id)
    )
    ''')

    # 5. Create the Drop Sources Table (Links items to Pals)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drop_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        pal_name TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    ''')

    # 6. Create the User Queues Table (Links items to user's build list)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_queues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        target_qty INTEGER NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    ''')

    # Save and close
    conn.commit()
    print("M2 Task 1 Complete: Relational schema tables created successfully!")
    conn.close()

if __name__ == "__main__":
    build_schema()