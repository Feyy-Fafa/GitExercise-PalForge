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

// ---// --- M1/M2 TASK 3 & 4: Persistent Interactive Build Queue ---
let activeQueue = [];
const queueDiv = document.getElementById('build-queue');

// Load the queue from the database when the app starts
async function loadQueueFromDB() {
    activeQueue = await eel.read_active_queue()();
    renderQueue();
}

// Add item to queue database (or increase quantity if it is already there)
window.addToQueue = async function(name) {
    await eel.add_to_queue_db(name)();
    await loadQueueFromDB();
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

// Queue management helper functions (DB Sync)
window.changeQty = async function(index, amount) {
    const itemName = activeQueue[index].name;
    await eel.update_queue_qty_db(itemName, amount)();
    await loadQueueFromDB();
}

window.removeFromQueue = async function(index) {
    const itemName = activeQueue[index].name;
    await eel.remove_from_queue_db(itemName)();
    await loadQueueFromDB();
}

// Boot up sequence: fetch the saved queue immediately
loadQueueFromDB();
// --- M1 TASK 4: Dynamic Crafting Tree & Farming Map UI ---
const calculateBtn = document.getElementById('calculate-btn');
const breakdownContainer = document.getElementById('material-breakdown');

// Listen for the user to click the "Calculate Base Materials" button
calculateBtn.addEventListener('click', async () => {
    // Check if the queue is empty before trying to calculate
    if (activeQueue.length === 0) {
        breakdownContainer.innerHTML = '<div class="placeholder-text">Please add items to your queue first.</div>';
        return;
    }

    // Show a loading state while Python does the math
    breakdownContainer.innerHTML = '<div class="placeholder-text">Calculating base materials...</div>';

    try {
        // The Bridge: Send the activeQueue array directly to the Python M3 engine
        // Python needs an @eel.expose function named 'calculate_recipe_tree'
        const calculatedData = await eel.calculate_recipe_tree(activeQueue)();
        
        // Pass the returned Python data to our rendering function
        renderMaterialBreakdown(calculatedData);
    } catch (error) {
        console.error("Backend error:", error);
        breakdownContainer.innerHTML = '<div class="placeholder-text" style="color: var(--palette-berry);">Error connecting to backend engine. Make sure Python is running.</div>';
    }
});

// Function to generate the UI components (Progress Bars & Drop Cards)
function renderMaterialBreakdown(data) {
    breakdownContainer.innerHTML = ''; // Clear the loading text

    if (!data || data.length === 0) {
        breakdownContainer.innerHTML = '<div class="placeholder-text">No materials required.</div>';
        return;
    }

    // Loop through the array Python hands back
    data.forEach((item, index) => {
        // Calculate a mock percentage for the visual progress bar
        const fakeProgress = Math.floor(Math.random() * 100); 

        // Build the drop source summary card using your CSS variables
        const dropSourceHtml = item.dropSource ? 
            `<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 8px; padding: 6px; background-color: var(--bg-void); border-radius: var(--border-radius-inner);">
                📍 <strong>Best Source:</strong> ${item.dropSource}
            </div>` : '';

        const stationHtml = item.station ? `<span class="station-tag">${item.station}</span>` : '';

        // Inject the HTML using your existing CSS classes
        breakdownContainer.innerHTML += `
            <div class="tree-node parent-node" style="flex-direction: column; align-items: flex-start;">
                <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                    <label for="mat-${index}" style="margin: 0;">
                        <input type="checkbox" id="mat-${index}"> 
                        ${item.name} 
                        ${stationHtml}
                    </label>
                    <span>x${item.quantity}</span>
                </div>
                
                <!-- M1 Task 4: Visual Progress Bar UI -->
                <div style="width: 100%; background: var(--bg-void); height: 8px; border-radius: 4px; margin-top: 10px; overflow: hidden;">
                    <div style="width: ${fakeProgress}%; background: var(--gradient-palette); height: 100%; border-radius: 4px;"></div>
                </div>
                
                <!-- M1 Task 4: Drop Source Summary Card UI -->
                ${dropSourceHtml}
            </div>
        `;
    });
}
// =====================================================================
// M1 TASK 5: INPUT VALIDATION & ERROR HANDLING
// =====================================================================

// 1. Setup the Toast Notification Container
const toastContainer = document.createElement('div');
toastContainer.className = 'toast-container';
document.body.appendChild(toastContainer);

window.showToast = function(message) {
    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.innerText = message;
    toastContainer.appendChild(toast);
    
    // Smoothly slide out and remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// 2. Override the Calculate Button (Empty Submission Guard)
const calcBtnElement = document.getElementById('calculate-btn');
if (calcBtnElement) {
    // We add this listener *before* the backend call happens
    calcBtnElement.addEventListener('click', (event) => {
        if (!activeQueue || activeQueue.length === 0) {
            event.stopImmediatePropagation(); // Kills the request before it hits Python
            showToast("⚠️ Cannot calculate: Your build queue is empty.");
        }
    }, true); // The 'true' captures the click first
}

// 3. Upgrade the Quantity Change Logic (Negative Quantity Guard)
// Replace your existing changeQty function with this validated version
window.changeQty = async function(index, amount) {
    const item = activeQueue[index];
    const newQty = item.qty + amount;

    if (newQty <= 0) {
        // Validation: Warn the user it's being deleted
        showToast(`🗑️ ${item.name} removed from queue.`);
        await eel.remove_from_queue_db(item.name)();
    } else if (newQty > 9999) {
        // Validation: Prevent ridiculous numbers breaking the math engine
        showToast("⚠️ Maximum item quantity exceeded.");
        return;
    } else {
        await eel.update_queue_qty_db(item.name, amount)();
    }
    
    await loadQueueFromDB();
}