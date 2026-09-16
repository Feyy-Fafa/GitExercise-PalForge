import sqlite3
import os

# Helper: Connect to your beautiful M2 database
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'palworld.db')
    return sqlite3.connect(db_path)

# Helper: Find an item's ID just by typing its name
def get_item_id(item_name, cursor):
    cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
    result = cursor.fetchone()
    return result[0] if result else None

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
        return {} # Failsafe if the item doesn't exist

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