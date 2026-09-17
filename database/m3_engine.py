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
        # If running as a bundled executable, save DB next to the .exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # If running normally via Python script
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


# =====================================================================
# M3 TASK 2: RECURSIVE BILL-OF-MATERIALS (BOM) ENGINE
# =====================================================================
def calculate_base_materials(item_name, quantity_needed=1):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        return _recursive_bom(item_name, quantity_needed, cursor)


# The actual recursive loop Ateya designed, upgraded for SQLite
def _recursive_bom(item_name, quantity_needed, cursor):
    item_id = get_item_id(item_name, cursor)
    if not item_id:
        return {}  # Failsafe if the item doesn't exist

    # Ask the database for the crafting recipe
    cursor.execute('''
        SELECT i.name, r.quantity 
        FROM recipes r
        JOIN items i ON r.ingredient_item_id = i.id
        WHERE r.crafted_item_id = ?
    ''', (item_id,))
    ingredients = cursor.fetchall()

    # BASE CASE: If the database returns nothing, it has no recipe. 
    # Therefore, it IS a raw material. Stop digging!
    if not ingredients:
        return {item_name: quantity_needed}

    # RECURSIVE CASE: It has a recipe! Break it down further.
    base_materials = {}
    for ing_name, ing_qty in ingredients:
        # Multiply by how many we are crafting
        total_ing_qty = ing_qty * quantity_needed
        
        # INCEPTION: The function calls itself to drill down to the next level
        sub_materials = _recursive_bom(ing_name, total_ing_qty, cursor)
        
        # Merge the dictionaries together
        for raw_mat, raw_qty in sub_materials.items():
            base_materials[raw_mat] = base_materials.get(raw_mat, 0) + raw_qty

    return base_materials


# =====================================================================
# M3 TASK 3: MULTI-PROJECT MATERIAL AGGREGATOR
# =====================================================================
def aggregate_queue(queue_items):
    """
    Takes a list of items (e.g., your build queue) and sums everything up 
    into one massive shopping list of base materials.
    """
    master_shopping_list = {}
    
    for item_name, qty in queue_items:
        # 1. Calculate the raw materials for this specific item
        item_materials = calculate_base_materials(item_name, qty)
        
        # 2. Add those materials to the master shopping list
        for raw_mat, raw_qty in item_materials.items():
            master_shopping_list[raw_mat] = master_shopping_list.get(raw_mat, 0) + raw_qty
            
    return master_shopping_list


# =====================================================================
# M3 TASK 4: EEL BRIDGE & DROP SOURCE MAPPER (For Frontend UI)
# =====================================================================
@eel.expose
def calculate_recipe_tree(js_queue):
    """
    Catches the frontend queue, translates it for the math engine, 
    and sends back formatted data for the UI progress bars and cards.
    """
    # 1. Translate JS objects into Python tuples for Ateya's aggregator
    python_queue = [(item['name'], item['qty']) for item in js_queue]
    
    # 2. Run the heavy recursive math
    raw_materials_dict = aggregate_queue(python_queue)
    
    # 3. Format the output back into a list of dictionaries for the Javascript UI
    formatted_results = []
    for mat_name, mat_qty in raw_materials_dict.items():
        # Placeholder drop logic so your UI renders properly today.
        # Ateya will update this to query the actual database drop tables later!
        mock_drop_source = f"Farm around starting biomes for {mat_name}"
        if mat_name == "Ore":
            mock_drop_source = "Desolate Church fast travel point (Red rocks)"
        elif mat_name == "Paldium Fragment":
            mock_drop_source = "Mine blue rocks near riverbanks"
            
        formatted_results.append({
            "name": mat_name,
            "quantity": mat_qty,
            "station": "Base",  # Placeholder
            "dropSource": mock_drop_source
        })
        
    return formatted_results


# =====================================================================
# THE FINAL TEST (Run this in the terminal!)
# =====================================================================
if __name__ == "__main__":
    print("--- TESTING M3 TASK 2: Recursive BOM ---")
    print("Materials for 1 Legendary Sphere:")
    print(calculate_base_materials("Legendary Sphere", 1))
    
    print("\n--- TESTING M3 TASK 3: Material Aggregator ---")
    # Simulating a user dropping 3 items into the frontend build queue
    player_queue = [
        ("Legendary Sphere", 5),
        ("Pal Metal Armor", 1),
        ("Ultra Sphere", 10)
    ]
    print("Total master shopping list for the queue:")
    print(aggregate_queue(player_queue))