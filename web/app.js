// --- M1 TASK 2: Item Database Search Interface ---
const searchBar = document.getElementById('search-bar');
const categoryFilter = document.getElementById('category-filter');
const resultsDiv = document.getElementById('item-results');

// Listen for user input
searchBar.addEventListener('input', fetchItems);
categoryFilter.addEventListener('change', fetchItems);

async function fetchItems() {
    const query = searchBar.value;
    const category = categoryFilter.value;
    
    // If search is empty, show the default placeholder
    if (query.length < 1) {
        resultsDiv.innerHTML = '<div class="placeholder-text">Type to search the database...</div>';
        return;
    }
    
    // Ask the Python backend for matching items (via Eel)
    const items = await eel.search_items(query, category)();
    
    resultsDiv.innerHTML = '';
    
    if (items.length === 0) {
        resultsDiv.innerHTML = '<div class="placeholder-text">No items found.</div>';
        return;
    }
    
    // Generate the CSS tree nodes for the search results
    items.forEach(itemName => {
        resultsDiv.innerHTML += `
            <div class="tree-node" style="justify-content: space-between;">
                <label style="padding-left:10px;">${itemName}</label>
                <button class="btn-primary" style="margin-top:0; padding: 6px 12px; width: auto;" onclick="addToQueue('${itemName}')">Add</button>
            </div>
        `;
    });
}

// --- M1 TASK 3: Interactive Build Queue ---
let activeQueue = [];
const queueDiv = document.getElementById('build-queue');

// Add item to queue (or increase quantity if it is already there)
window.addToQueue = function(name) {
    const existing = activeQueue.find(i => i.name === name);
    if (existing) {
        existing.qty++;
    } else {
        activeQueue.push({ name: name, qty: 1 });
    }
    renderQueue();
}

// Update the middle UI panel
function renderQueue() {
    queueDiv.innerHTML = '';
    
    if (activeQueue.length === 0) {
        queueDiv.innerHTML = '<div class="placeholder-text">Your queue is empty.</div>';
        return;
    }
    
    activeQueue.forEach((item, idx) => {
        queueDiv.innerHTML += `
            <div class="tree-node" style="justify-content: space-between;">
                <label style="padding-left:10px;">${item.name} <span>x${item.qty}</span></label>
                <div style="display: flex; gap: 10px;">
                    <button onclick="changeQty(${idx}, 1)" style="background:transparent; border:none; color:var(--palette-gold); cursor:pointer; font-weight:bold; font-size:1.2rem;">+</button>
                    <button onclick="changeQty(${idx}, -1)" style="background:transparent; border:none; color:var(--palette-gold); cursor:pointer; font-weight:bold; font-size:1.2rem;">-</button>
                    <button onclick="removeFromQueue(${idx})" style="background:transparent; border:none; color:var(--palette-berry); cursor:pointer; font-weight:bold; font-size:1.2rem;">X</button>
                </div>
            </div>
        `;
    });
}

// Queue management helper functions
window.changeQty = function(index, amount) {
    activeQueue[index].qty += amount;
    if (activeQueue[index].qty <= 0) {
        removeFromQueue(index);
    } else {
        renderQueue();
    }
}

window.removeFromQueue = function(index) {
    activeQueue.splice(index, 1);
    renderQueue();
}