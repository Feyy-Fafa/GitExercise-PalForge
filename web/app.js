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
    
    // 1. Check if we have a saved calculated tree from a previous visit
    const savedTree = localStorage.getItem('calculatedTreeData');
    if (savedTree) {
        renderMaterialBreakdown(JSON.parse(savedTree));
    } else {
        // 2. If no tree is calculated, just send the top-level queue to the drop map
        const neededItemsArray = activeQueue.map(item => item.name);
        localStorage.setItem('activeQueueItems', JSON.stringify(neededItemsArray));
    }
}

// Wipes the saved math if you change your queue
function wipeTreeData() {
    localStorage.removeItem('calculatedTreeData');
    const breakdownContainer = document.getElementById('material-breakdown');
    if (breakdownContainer) {
        breakdownContainer.innerHTML = '<div class="placeholder-text">Queue updated. Please click Calculate again.</div>';
    }
}

window.addToQueue = async function(name) {
    await eel.add_to_queue_db(name)();
    wipeTreeData();
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
    wipeTreeData();
    await loadQueueFromDB();
}

window.removeFromQueue = async function(index) {
    const itemName = activeQueue[index].name;
    // Trigger the notification
    showToast(`🗑️ ${itemName} removed from queue.`);
    await eel.remove_from_queue_db(itemName)();
    wipeTreeData();
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
           
            // SAVE THE TREE: Keeps it on the screen if you leave and come back
            localStorage.setItem('calculatedTreeData', JSON.stringify(calculatedData));

            // DEEP HIGHLIGHTING: Grab every single raw material from the tree for the drop map
            const allNeededItems = new Set();
            function extractItems(node) {
                allNeededItems.add(node.name);
                if (node.children) {
                    node.children.forEach(extractItems);
                }
            }
            calculatedData.forEach(extractItems);
            
            // Send this massive list to the drop manager
            localStorage.setItem('activeQueueItems', JSON.stringify(Array.from(allNeededItems)));
            showToast("✅ Calculation complete! Materials highlighted in Drop Maps.");
            
        } catch (error) {
            console.error("Backend error:", error);
            breakdownContainer.innerHTML = '<div class="placeholder-text" style="color: var(--palette-berry);">Error connecting to backend engine. Make sure Python is running.</div>';
        }
    });
}

function renderMaterialBreakdown(data) {
    const breakdownContainer = document.getElementById('material-breakdown');
    if (!breakdownContainer) return; // safeguard if called on the wrong page
    
    breakdownContainer.innerHTML = ''; 

    if (!data || data.length === 0) {
        breakdownContainer.innerHTML = '<div class="placeholder-text">No materials required.</div>';
        return;
    }

    data.forEach(rootItem => {
        breakdownContainer.appendChild(createTreeNode(rootItem));
    });
}

function createTreeNode(item) {
    const wrapper = document.createElement('div');
    wrapper.className = 'tree-hierarchy';
    
    // Check if the item actually has raw materials underneath it
    const hasChildren = item.children && item.children.length > 0;
    const toggleIcon = hasChildren ? `<span class="toggle-icon">▼</span>` : `<span class="empty-icon"></span>`;

    // Only make the row clickable if it has children
    const clickHandler = hasChildren ? `onclick="toggleNode(this)"` : '';

    const nodeHtml = `
        <div class="tree-node parent-node" ${clickHandler} style="cursor: ${hasChildren ? 'pointer' : 'default'}; user-select: none;">
            <label style="display: flex; align-items: center; gap: 8px; margin: 0; cursor: inherit;">
                ${toggleIcon}
                <input type="checkbox" style="width: 16px; height: 16px;" onclick="event.stopPropagation();"> 
                ${item.name}
            </label>
            <span style="color: var(--palette-gold); font-weight: bold;">x${item.quantity}</span>
        </div>
    `;
    wrapper.innerHTML = nodeHtml;
    
    if (hasChildren) {
        const childrenContainer = document.createElement('div');
        // Add 'collapsible-content' for our CSS to target
        childrenContainer.className = 'tree-children collapsible-content'; 
        
        item.children.forEach(child => {
            childrenContainer.appendChild(createTreeNode(child));
        });
        
        wrapper.appendChild(childrenContainer);
    }
    
    return wrapper;
}

// Global function to handle the open/close animation
window.toggleNode = function(element) {
    const childrenContainer = element.nextElementSibling;
    const icon = element.querySelector('.toggle-icon');
    
    if (childrenContainer && childrenContainer.classList.contains('collapsible-content')) {
        // Toggle the hidden class
        childrenContainer.classList.toggle('collapsed');
        // Rotate the arrow icon
        if (icon) {
            icon.classList.toggle('rotated');
        }
    }
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