// =====================================================================
// M1 TASK 2: Item Database Search Interface
// =====================================================================
const searchBar = document.getElementById('search-bar');
const categoryFilter = document.getElementById('category-filter');
const resultsDiv = document.getElementById('item-results');

searchBar.addEventListener('input', fetchItems);
categoryFilter.addEventListener('change', fetchItems);

async function fetchItems() {
    const query = searchBar.value;
    const category = categoryFilter.value;
    
    if (query.length < 1) {
        resultsDiv.innerHTML = '<div class="placeholder-text">Type to search the database...</div>';
        return;
    }
    
    // Pass both query and category to Python
    const items = await eel.search_items(query, category)();
    
    resultsDiv.innerHTML = '';
    
    if (items.length === 0) {
        resultsDiv.innerHTML = '<div class="placeholder-text">No items found.</div>';
        return;
    }
    
    items.forEach(item => {
        resultsDiv.innerHTML += `
            <div class="tree-node" style="justify-content: space-between;">
                <label style="padding-left:10px;">${item.name}</label>
                <button class="btn-primary" style="margin-top:0; padding: 6px 12px; width: auto;" onclick="addToQueue('${item.name}')">Add</button>
            </div>
        `;
    });
}

// =====================================================================
// M1/M2 TASK 3 & 4: Persistent Interactive Build Queue
// =====================================================================
let activeQueue = [];
const queueDiv = document.getElementById('build-queue');

async function loadQueueFromDB() {
    activeQueue = await eel.read_active_queue()();
    renderQueue();
}

window.addToQueue = async function(name) {
    await eel.add_to_queue_db(name)();
    await loadQueueFromDB();
}

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

window.changeQty = async function(index, amount) {
    const item = activeQueue[index];
    const newQty = item.qty + amount;

    if (newQty <= 0) {
        showToast(`🗑️ ${item.name} removed from queue.`);
        await eel.remove_from_queue_db(item.name)();
    } else if (newQty > 9999) {
        showToast("⚠️ Maximum item quantity exceeded.");
        return;
    } else {
        await eel.update_queue_qty_db(item.name, amount)();
    }
    await loadQueueFromDB();
}

window.removeFromQueue = async function(index) {
    const itemName = activeQueue[index].name;
    await eel.remove_from_queue_db(itemName)();
    await loadQueueFromDB();
}

loadQueueFromDB();

// =====================================================================
// M1 TASK 4: Dynamic Crafting Tree & Farming Map UI
// =====================================================================
const calculateBtn = document.getElementById('calculate-btn');
const breakdownContainer = document.getElementById('material-breakdown');

if (calculateBtn) {
    calculateBtn.addEventListener('click', async (event) => {
        if (!activeQueue || activeQueue.length === 0) {
            event.stopImmediatePropagation();
            showToast("⚠️ Cannot calculate: Your build queue is empty.");
            breakdownContainer.innerHTML = '<div class="placeholder-text">Please add items to your queue first.</div>';
            return;
        }

        breakdownContainer.innerHTML = '<div class="placeholder-text">Calculating base materials...</div>';

        try {
            const calculatedData = await eel.calculate_recipe_tree(activeQueue)();
            renderMaterialBreakdown(calculatedData);
        } catch (error) {
            console.error("Backend error:", error);
            breakdownContainer.innerHTML = '<div class="placeholder-text" style="color: var(--palette-berry);">Error connecting to backend engine. Make sure Python is running.</div>';
        }
    });
}

function renderMaterialBreakdown(data) {
    breakdownContainer.innerHTML = ''; 

    if (!data || data.length === 0) {
        breakdownContainer.innerHTML = '<div class="placeholder-text">No materials required.</div>';
        return;
    }

    data.forEach((item, index) => {
        const fakeProgress = Math.floor(Math.random() * 100); 

        const dropSourceHtml = item.dropSource ? 
            `<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 8px; padding: 6px; background-color: var(--bg-void); border-radius: var(--border-radius-inner);">
                📍 <strong>Best Source:</strong> ${item.dropSource}
            </div>` : '';

        const stationHtml = item.station ? `<span class="station-tag">${item.station}</span>` : '';

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
                
                <div style="width: 100%; background: var(--bg-void); height: 8px; border-radius: 4px; margin-top: 10px; overflow: hidden;">
                    <div style="width: ${fakeProgress}%; background: var(--gradient-palette); height: 100%; border-radius: 4px;"></div>
                </div>
                
                ${dropSourceHtml}
            </div>
        `;
    });
}

// =====================================================================
// M1 TASK 5: INPUT VALIDATION & ERROR HANDLING (TOASTS)
// =====================================================================
const toastContainer = document.createElement('div');
toastContainer.className = 'toast-container';
document.body.appendChild(toastContainer);

window.showToast = function(message) {
    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.innerText = message;
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}