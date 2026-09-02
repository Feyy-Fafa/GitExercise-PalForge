# 1. THE DATA MODEL (Mock Database)
# This dictionary represents how recipes are structured before hitting a real database.
# Craftable items are keys; their values are dictionaries of ingredients.
palforge_recipes = {
    "Hyper Sphere": {
        "Paldium Fragment": 3,
        "Ingot": 3,
        "Wood": 8
    },
    "Ingot": {
        "Ore": 2  # 1 Ingot requires 2 Ore
    }
    # Notice: Wood, Paldium Fragment, and Ore are NOT keys here. 
    # That is because they are base materials (they have no recipe).
}

# 2. THE RECURSIVE ALGORITHM
def calculate_base_materials(item_name, quantity_needed=1):
    """
    Recursively breaks down an item into its rawest base materials.
    """
    # BASE CASE (The Stopping Point): 
    # If the item doesn't have a recipe, it IS a raw material. Stop digging.
    if item_name not in palforge_recipes:
        return {item_name: quantity_needed}

    # RECURSIVE CASE (The Loop):
    # If the item has a recipe, break it down further.
    base_materials = {}
    recipe = palforge_recipes[item_name]
    
    for ingredient, ingredient_qty in recipe.items():
        # Multiply the recipe requirement by how many we are trying to craft
        total_ingredient_qty = ingredient_qty * quantity_needed
        
        # RECURSION: The function calls ITSELF to break down the ingredient
        sub_materials = calculate_base_materials(ingredient, total_ingredient_qty)
        
        # MERGE: Combine the returned sub-materials into our main dictionary
        for raw_mat, raw_qty in sub_materials.items():
            if raw_mat in base_materials:
                base_materials[raw_mat] += raw_qty
            else:
                base_materials[raw_mat] = raw_qty
                
    return base_materials

# 3. EXECUTING AND STRUCTURING THE FINAL OUTPUT
target_item = "Hyper Sphere"
amount_to_craft = 1

# This is the final dictionary structure that your frontend will receive
final_output = {
    "Item": target_item,
    "Total_Crafted": amount_to_craft,
    "Raw_Materials": calculate_base_materials(target_item, amount_to_craft)
}

print(final_output)