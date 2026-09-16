import sqlite3
import os

# Helper function to connect to the database
def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'palworld.db')
    return sqlite3.connect(db_path)

# --- M2 TASK 3 REQUIRED FUNCTIONS ---

# 1. Get an item exactly by its ID
def get_item_by_id(item_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        return cursor.fetchone()

# 2. Search for items (Fairos's search bar will use this)
def search_items(keyword):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category FROM items WHERE name LIKE ?", (f'%{keyword}%',))
        return cursor.fetchall()

# 3. Filter items by type (Matches the Notion Card exactly)
def filter_by_type(item_type):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category FROM items WHERE category = ?", (item_type,))
        return cursor.fetchall()

# --- M3 PREP (For Ateya's Math Engine) ---

# 4. Get all ingredients required to craft an item
def get_recipe(item_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.name, r.quantity 
            FROM recipes r
            JOIN items i ON r.ingredient_item_id = i.id
            WHERE r.crafted_item_id = ?
        ''', (item_id,))
        return cursor.fetchall()

# --- QUICK TEST (Run this to prove it works!) ---
if __name__ == "__main__":
    print("--- TESTING SEARCH ENGINE ---")
    print("Searching for 'Armor':", search_items('Armor'))
    
    print("\n--- TESTING TYPE FILTER ---")
    print("Filtering for 'spheres':", filter_by_type('spheres'))
    
    print("\n--- TESTING RECIPE PULL (For Ateya) ---")
    # Using ID 30, which should be the Legendary Sphere based on our injection order
    print("Ingredients for item ID 30:", get_recipe(30))