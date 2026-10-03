import eel
import sqlite3
import json
import os
import sys
import urllib.request
from collections import defaultdict
from database import m3_engine

# Initialize the web folder for Eel
eel.init('web')

# Determine correct path whether running as script or compiled .exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

LOCAL_DB_PATH = os.path.join(application_path, 'items.json')

def fetch_remote_database():
    """Pulls the latest items.json from the GitHub raw URL on startup"""
    remote_url = "https://raw.githubusercontent.com/Feyy-Fafa/GitExercise-PalForge/main/items.json"
    try:
        urllib.request.urlretrieve(remote_url, LOCAL_DB_PATH)
        print("Successfully updated item database from remote source!")
    except Exception as e:
        print("Offline or unable to reach remote database. Using local copy.", e)

def load_item_database():
    fetch_remote_database()
    if os.path.exists(LOCAL_DB_PATH):
        with open(LOCAL_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@eel.expose
def fetch_external_search_items(query, category):
    database = load_item_database()
    results = []
    seen_items = set() 
    
    query_lower = query.lower()
    
    # Normalize the category: make it lowercase and remove the trailing 's'
    if category and category != "all":
        category_target = category.lower().rstrip('s')
    else:
        category_target = "all"
    
    # 1. Search the JSON Database
    for item_name, item_data in database.items():
        # Clean the JSON category the exact same way
        item_cat = item_data.get("category", "General").lower().rstrip('s')
        
        if query_lower in item_name.lower():
            if category_target == "all" or item_cat == category_target:
                results.append({
                    "name": item_data.get("name", item_name),
                    "category": item_data.get("category", "General")
                })
                seen_items.add(item_name.lower())
                
    # 2. Search the SQLite Database
    try:
        conn = sqlite3.connect('database/palworld.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, category FROM items")
        db_items = cursor.fetchall()
        conn.close()
        
        for name, db_category in db_items:
            # Clean the SQLite category
            db_cat = (db_category or "General").lower().rstrip('s')
            
            if query_lower in name.lower() and name.lower() not in seen_items:
                if category_target == "all" or db_cat == category_target:
                    results.append({
                        "name": name,
                        "category": db_category
                    })
    except Exception as e:
        print("Database search error:", e)
                
    return results

@eel.expose
def calculate_external_recipe_tree(active_queue):
    database = load_item_database()
    visual_tree = []
    
    try:
        conn = sqlite3.connect('database/palworld.db')
        cursor = conn.cursor()
        
        # Helper 1: Fetches from SQLite
        def get_db_children(current_name):
            cursor.execute('''
                SELECT ingredient.name, recipes.quantity
                FROM recipes
                JOIN items AS crafted ON recipes.crafted_item_id = crafted.id
                JOIN items AS ingredient ON recipes.ingredient_item_id = ingredient.id
                WHERE crafted.name = ?
            ''', (current_name,))
            
            db_rows = cursor.fetchall()
            child_list = []
            for ing_name, ing_qty in db_rows:
                child_list.append({
                    "name": ing_name,
                    "quantity": ing_qty,
                    "children": build_node(ing_name) # Recursively dig deeper
                })
            return child_list

        # Helper 2: Decides whether to use JSON or SQLite for a specific item
        def build_node(item_name):
            # 1. Check if the item is a top-level override in JSON
            item_info = database.get(item_name)
            
            # If JSON explicitly defines children, process them
            if item_info and "children" in item_info and len(item_info["children"]) > 0:
                json_children = []
                for child in item_info["children"]:
                    json_children.append({
                        "name": child["name"],
                        "quantity": child["quantity"],
                        "children": build_node(child["name"]) # Let the engine check if these children can break down further
                    })
                return json_children
            
            # 2. If it's not in JSON (or has empty children), check SQLite
            return get_db_children(item_name)

        # Main Loop: Process the user's cart
        for queue_item in active_queue:
            item_name = queue_item["name"]
            item_qty = queue_item["qty"]
            
            node = {
                "name": item_name,
                "quantity": item_qty,
                "children": build_node(item_name)
            }
            visual_tree.append(node)
            
        conn.close()
    except Exception as e:
        print("Calculation error:", e)
        
    return {"visual_tree": visual_tree}

@eel.expose
def get_all_drop_sources():
    conn = sqlite3.connect('database/palworld.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT item_name, source FROM drop_sources ORDER BY item_name ASC")
    rows = cursor.fetchall()
    conn.close()

    grouped_sources = defaultdict(list)
    for item_name, source in rows:
        grouped_sources[item_name].append(source)
        
    return dict(grouped_sources)

# Start the application
if __name__ == '__main__':
    # 1. Run the web server check BEFORE the UI loads
    m3_engine.check_for_updates()
    
    # 2. Start the Eel window
    eel.start('index.html', size=(1200, 800))