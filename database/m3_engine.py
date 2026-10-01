import os
import sys
import sqlite3
import eel

# Helper: Find an item's ID just by typing its name
def get_item_id(item_name, cursor):
    cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
    result = cursor.fetchone()
    return result[0] if result else None

# =====================================================================
# M2 TASK 5: DATABASE OPTIMIZATION, ERROR HANDLING & PACKAGING PREP
# =====================================================================
def get_db_path():
    """Ensures the SQLite DB is saved locally and survives PyInstaller packaging."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_dir, 'palworld.db')

def get_db_connection():
    """Establishes connection using the dynamic packaging path."""
    return sqlite3.connect(get_db_path())

def init_queue_table():
    """Ensures the build_queue table exists in the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS build_queue (
                    item_name TEXT PRIMARY KEY,
                    quantity INTEGER NOT NULL
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to initialize table: {e}")

# Run this once when the engine starts
init_queue_table()

@eel.expose
def add_to_queue_db(item_name):
    """CREATE/UPDATE: Adds an item, or increments if it already exists."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO build_queue (item_name, quantity)
                VALUES (?, 1)
                ON CONFLICT(item_name) DO UPDATE SET quantity = quantity + 1
            ''', (item_name,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to add {item_name}: {e}")

@eel.expose
def update_queue_qty_db(item_name, change_amount):
    """UPDATE/DELETE: Adjusts quantity. Deletes item if quantity hits 0."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE build_queue
                SET quantity = quantity + ?
                WHERE item_name = ?
            ''', (change_amount, item_name))
            cursor.execute('DELETE FROM build_queue WHERE quantity <= 0')
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to update {item_name}: {e}")

@eel.expose
def remove_from_queue_db(item_name):
    """DELETE: Completely removes an item from the queue."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM build_queue WHERE item_name = ?', (item_name,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to remove {item_name}: {e}")

@eel.expose
def read_active_queue():
    """READ: Fetches the saved queue for the frontend on startup."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT item_name, quantity FROM build_queue')
            rows = cursor.fetchall()
            return [{"name": row[0], "qty": row[1]} for row in rows]
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to read queue: {e}")
        return []

@eel.expose
def search_items(query, category="all"):
    """READ: Fetches items matching the frontend search query and category filter."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if category == "all":
                cursor.execute(
                    "SELECT name FROM items WHERE name LIKE ? LIMIT 20", 
                    (f'%{query}%',)
                )
            else:
                # Assuming 'category' column exists in your items table.
                cursor.execute(
                    "SELECT name FROM items WHERE name LIKE ? AND category = ? LIMIT 20", 
                    (f'%{query}%', category)
                )
                
            rows = cursor.fetchall()
            return [{"name": row[0]} for row in rows] 
            
    except sqlite3.Error as e:
        print(f"[DB ERROR] Search failed: {e}")
        return []

# =====================================================================
# M3 TASK 2: RECURSIVE BILL-OF-MATERIALS (BOM) ENGINE
# =====================================================================
def calculate_base_materials(item_name, quantity_needed=1):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        return _recursive_bom(item_name, quantity_needed, cursor)

def _recursive_bom(item_name, quantity_needed, cursor):
    item_id = get_item_id(item_name, cursor)
    if not item_id:
        return {}

    cursor.execute('''
        SELECT i.name, r.quantity 
        FROM recipes r
        JOIN items i ON r.ingredient_item_id = i.id
        WHERE r.crafted_item_id = ?
    ''', (item_id,))
    ingredients = cursor.fetchall()

    if not ingredients:
        return {item_name: quantity_needed}

    base_materials = {}
    for ing_name, ing_qty in ingredients:
        total_ing_qty = ing_qty * quantity_needed
        sub_materials = _recursive_bom(ing_name, total_ing_qty, cursor)
        
        for raw_mat, raw_qty in sub_materials.items():
            base_materials[raw_mat] = base_materials.get(raw_mat, 0) + raw_qty

    return base_materials

# =====================================================================
# M3 TASK 3: MULTI-PROJECT MATERIAL AGGREGATOR
# =====================================================================
def aggregate_queue(queue_items):
    master_shopping_list = {}
    for item_name, qty in queue_items:
        item_materials = calculate_base_materials(item_name, qty)
        for raw_mat, raw_qty in item_materials.items():
            master_shopping_list[raw_mat] = master_shopping_list.get(raw_mat, 0) + raw_qty
    return master_shopping_list

# =====================================================================
# M3 TASK 4: EEL BRIDGE & RECURSIVE TREE GENERATOR (For Frontend UI)
# =====================================================================
@eel.expose
def calculate_recipe_tree(js_queue):
    tree_results = []
    queue_tuples = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for item in js_queue:
            # Build the nested tree for Fairos's Accordion UI
            tree_results.append(_build_nested_tree(item['name'], item['qty'], cursor))
            # Prep the tuple format needed for the aggregator
            queue_tuples.append((item['name'], item['qty']))
            
    # 1. Get total raw materials using Ateya's existing aggregator
    total_raw_materials = aggregate_queue(queue_tuples)
    
    # 2. Get user's current inventory using Noor's new database function
    current_inventory = get_inventory_db()
    
    # 3. Calculate deficit (Ateya's core mathematical upgrade)
    deficit_materials = {}
    for item, total_needed in total_raw_materials.items():
        owned = current_inventory.get(item, 0)
        still_need = total_needed - owned
        
        # Only add to the deficit list if the user doesn't have enough
        if still_need > 0:
            deficit_materials[item] = still_need
            
    # Pass the multi-part payload back across the Eel bridge
    return {
        "visual_tree": tree_results,
        "deficit_totals": deficit_materials,
        "total_raw_materials": total_raw_materials
    }
def _build_nested_tree(item_name, qty, cursor):
    # Create the current node
    node = {"name": item_name, "quantity": qty, "children": []}
    
    item_id = get_item_id(item_name, cursor)
    if not item_id: 
        return node
        
    # Get ingredients
    cursor.execute('''
        SELECT i.name, r.quantity 
        FROM recipes r
        JOIN items i ON r.ingredient_item_id = i.id
        WHERE r.crafted_item_id = ?
    ''', (item_id,))
    ingredients = cursor.fetchall()
    
    # Recursively fetch children
    for ing_name, ing_qty in ingredients:
        total_ing_qty = ing_qty * qty
        node["children"].append(_build_nested_tree(ing_name, total_ing_qty, cursor))
        
    return node
        
    

@eel.expose
def update_inventory_db(item_name, quantity):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if quantity <= 0:
            cursor.execute("DELETE FROM inventory WHERE item_name = ?", (item_name,))
        else:
            cursor.execute('''
                INSERT INTO inventory (item_name, quantity) 
                VALUES (?, ?)
                ON CONFLICT(item_name) DO UPDATE SET quantity = ?
            ''', (item_name, quantity, quantity))
        conn.commit()

@eel.expose
def get_inventory_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, quantity FROM inventory")
        return {row[0]: row[1] for row in cursor.fetchall()}

if __name__ == "__main__":
    print("--- TESTING M3 TASK 2: Recursive BOM ---")
    print("Materials for 1 Legendary Sphere:")
    print(calculate_base_materials("Legendary Sphere", 1))
    
    print("\n--- TESTING M3 TASK 3: Material Aggregator ---")
    player_queue = [
        ("Legendary Sphere", 5),
        ("Pal Metal Armor", 1),
        ("Ultra Sphere", 10)
    ]
    print("Total master shopping list for the queue:")
    print(aggregate_queue(player_queue))

    