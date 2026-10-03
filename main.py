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
    remote_url = "https://raw.githubusercontent.com/Feyy-Fafa/GitExercise-PalForge/ui-refractor-updates/items.json"
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
    
    query = query.lower()
    for item_name, item_data in database.items():
        if query in item_name.lower():
            if not category or category == "all" or item_data.get("category") == category:
                results.append({
                    "name": item_data.get("name", item_name),
                    "category": item_data.get("category", "General")
                })
                
    return results

@eel.expose
def calculate_external_recipe_tree(active_queue):
    database = load_item_database()
    visual_tree = []
    
    for queue_item in active_queue:
        item_name = queue_item["name"]
        item_qty = queue_item["qty"]
        
        item_info = database.get(item_name, {})
        
        node = {
            "name": item_name,
            "quantity": item_qty,
            "children": item_info.get("children", [])
        }
        visual_tree.append(node)
        
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