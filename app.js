const API_URL = 'http://127.0.0.1:8000/api';

// Application State
let coffeesState = [];
let currentCategoryFilter = 'all';
let currentSearchQuery = '';
let currentSortBy = 'votes';

// DOM Elements
const coffeeGrid = document.getElementById('coffeeGrid');
const loadingGrid = document.getElementById('loadingGrid');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const categoriesFilter = document.getElementById('categoriesFilter');
const sortSelect = document.getElementById('sortSelect');

// Stats Elements
const statTotalBrews = document.getElementById('statTotalBrews');
const statTotalVotes = document.getElementById('statTotalVotes');
const statTopBrew = document.getElementById('statTopBrew');

// Modal Elements
const addCoffeeModal = document.getElementById('addCoffeeModal');
const openAddModalBtn = document.getElementById('openAddModalBtn');
const closeAddModalBtn = document.getElementById('closeAddModalBtn');
const cancelAddModalBtn = document.getElementById('cancelAddModalBtn');
const addCoffeeForm = document.getElementById('addCoffeeForm');
const formErrorMessage = document.getElementById('formErrorMessage');
const emptyStateAddBtn = document.getElementById('emptyStateAddBtn');

// Reset Button
const resetDbBtn = document.getElementById('resetDbBtn');

// Initialize Lucide Icons on start
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    fetchCoffees();
});

// Toast Notification System
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'toast-error' : 'toast-success'}`;
    
    // Choose icon based on type
    const iconName = type === 'error' ? 'alert-triangle' : 'check-circle';
    toast.innerHTML = `
        <i data-lucide="${iconName}"></i>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    lucide.createIcons(); // Initialize the new icon
    
    // Animate and remove
    setTimeout(() => {
        toast.classList.add('toast-fade-out');
        setTimeout(() => {
            toast.remove();
        }, 350);
    }, 3500);
}

// Fetch all coffees from API
async function fetchCoffees() {
    showLoading(true);
    try {
        const response = await fetch(`${API_URL}/coffees`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        coffeesState = await response.json();
        renderCoffees();
        updateStats();
    } catch (error) {
        console.error('Failed to fetch coffees:', error);
        showToast('Cannot connect to the Coffee Server. Make sure the backend is running.', 'error');
        showLoading(false);
        coffeeGrid.style.display = 'none';
        emptyState.style.display = 'block';
    }
}

// Control visibility of loaders and states
function showLoading(isLoading) {
    if (isLoading) {
        loadingGrid.style.display = 'grid';
        coffeeGrid.style.display = 'none';
        emptyState.style.display = 'none';
    } else {
        loadingGrid.style.display = 'none';
    }
}

// Compute and update stats header bar
function updateStats() {
    if (coffeesState.length === 0) {
        statTotalBrews.textContent = '0';
        statTotalVotes.textContent = '0';
        statTopBrew.textContent = 'None';
        return;
    }
    
    const totalBrews = coffeesState.length;
    const totalVotes = coffeesState.reduce((sum, item) => sum + item.votes, 0);
    
    // Find item with max votes
    let topBrew = coffeesState.reduce((max, item) => (item.votes > max.votes ? item : max), coffeesState[0]);
    
    statTotalBrews.textContent = totalBrews;
    statTotalVotes.textContent = totalVotes;
    statTopBrew.textContent = topBrew.votes > 0 ? topBrew.name : 'None';
}

// Render coffees to the grid based on filters and sorting
function renderCoffees() {
    showLoading(false);
    
    // 1. Filter
    let filteredCoffees = coffeesState.filter(coffee => {
        const matchesSearch = coffee.name.toLowerCase().includes(currentSearchQuery) || 
                              coffee.description.toLowerCase().includes(currentSearchQuery);
        
        const matchesCategory = currentCategoryFilter === 'all' || 
                                coffee.category === currentCategoryFilter;
                                
        return matchesSearch && matchesCategory;
    });
    
    // 2. Sort
    filteredCoffees.sort((a, b) => {
        if (currentSortBy === 'votes') {
            if (b.votes !== a.votes) {
                return b.votes - a.votes; // Primary: votes desc
            }
            return a.name.localeCompare(b.name); // Secondary: alphabetical
        } else {
            return a.name.localeCompare(b.name); // Alphabetical
        }
    });

    // Check empty state
    if (filteredCoffees.length === 0) {
        coffeeGrid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    coffeeGrid.style.display = 'grid';
    
    // Map of rankings based on global vote standing
    // To make rank badges correct regardless of current alphabetical view, we compute sorted order
    const globalSortedIds = [...coffeesState]
        .sort((a, b) => b.votes - a.votes || a.name.localeCompare(b.name))
        .map(c => c.id);

    coffeeGrid.innerHTML = '';
    
    filteredCoffees.forEach(coffee => {
        // Calculate global rank
        const rankIndex = globalSortedIds.indexOf(coffee.id);
        const rank = rankIndex + 1;
        
        let rankClass = 'rank-other';
        if (rank === 1) rankClass = 'rank-1';
        else if (rank === 2) rankClass = 'rank-2';
        else if (rank === 3) rankClass = 'rank-3';
        
        // Map category style class
        let categoryClass = 'cat-bold';
        if (coffee.category === 'Creamy & Balanced') categoryClass = 'cat-creamy';
        else if (coffee.category === 'Sweet & Smooth') categoryClass = 'cat-sweet';
        else if (coffee.category === 'Cold & Refreshing') categoryClass = 'cat-cold';

        const card = document.createElement('div');
        card.className = 'coffee-card';
        card.dataset.id = coffee.id;
        
        card.innerHTML = `
            <div class="rank-badge ${rankClass}">#${rank}</div>
            <div class="category-badge ${categoryClass}">${coffee.category}</div>
            <div class="card-image-container">
                <img src="${coffee.image_path}" alt="${coffee.name}" class="coffee-image" onerror="this.src='images/espresso.png'">
            </div>
            <div class="card-details">
                <h3 class="coffee-title">${coffee.name}</h3>
                <p class="coffee-desc">${coffee.description}</p>
                <div class="card-action-bar">
                    <div class="vote-info">
                        <span class="vote-number" id="voteCount-${coffee.id}">${coffee.votes}</span>
                        <span class="vote-label">Votes</span>
                    </div>
                    <button class="vote-btn" onclick="handleVoteClick(event, ${coffee.id})" aria-label="Vote for ${coffee.name}">
                        <i data-lucide="heart"></i>
                    </button>
                </div>
            </div>
        `;
        
        coffeeGrid.appendChild(card);
    });
    
    // Reinitialize newly added Lucide icons
    lucide.createIcons();
}

// Handle voting click
async function handleVoteClick(event, id) {
    event.preventDefault();
    const btn = event.currentTarget;
    btn.disabled = true; // Prevent double taps during request
    
    try {
        const response = await fetch(`${API_URL}/coffees/${id}/vote`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Voting failed');
        }
        
        const updatedCoffee = await response.json();
        
        // Update local state
        const idx = coffeesState.findIndex(c => c.id === id);
        if (idx !== -1) {
            coffeesState[idx].votes = updatedCoffee.votes;
        }
        
        // Animate the vote count change directly for instant feedback
        const voteEl = document.getElementById(`voteCount-${id}`);
        if (voteEl) {
            voteEl.textContent = updatedCoffee.votes;
            voteEl.classList.add('pop-active');
            
            // Remove animation class after animation completes
            setTimeout(() => {
                voteEl.classList.remove('pop-active');
            }, 400);
        }
        
        showToast(`Vote recorded for ${updatedCoffee.name}!`);
        updateStats();
        
        // Re-render after a tiny delay so user sees the anim before list reorders (if sorted by votes)
        setTimeout(() => {
            renderCoffees();
        }, 500);
        
    } catch (error) {
        console.error('Error voting:', error);
        showToast('Could not register vote. Try again later.', 'error');
        btn.disabled = false;
    }
}

// Category Filter Click
categoriesFilter.addEventListener('click', (e) => {
    if (e.target.classList.contains('filter-btn')) {
        // Toggle active button
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        currentCategoryFilter = e.target.dataset.category;
        renderCoffees();
    }
});

// Search input listener
searchInput.addEventListener('input', (e) => {
    currentSearchQuery = e.target.value.toLowerCase().trim();
    renderCoffees();
});

// Sort select listener
sortSelect.addEventListener('change', (e) => {
    currentSortBy = e.target.value;
    renderCoffees();
});

// Modal Actions
openAddModalBtn.addEventListener('click', () => {
    addCoffeeModal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Lock background scroll
    document.getElementById('coffeeName').focus();
});

function closeModal() {
    addCoffeeModal.style.display = 'none';
    document.body.style.overflow = ''; // Unlock scroll
    addCoffeeForm.reset();
    formErrorMessage.style.display = 'none';
}

closeAddModalBtn.addEventListener('click', closeModal);
cancelAddModalBtn.addEventListener('click', closeModal);
emptyStateAddBtn.addEventListener('click', () => {
    openAddModalBtn.click();
});

// Handle click outside modal content to close
addCoffeeModal.addEventListener('click', (e) => {
    if (e.target === addCoffeeModal) {
        closeModal();
    }
});

// Submit Form Handler
addCoffeeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('coffeeName').value.trim();
    const category = document.getElementById('coffeeCategory').value;
    const description = document.getElementById('coffeeDescription').value.trim();
    
    // Find active image radio choice
    const imageChoice = document.querySelector('input[name="imageChoice"]:checked').value;
    
    // Clear previous error
    formErrorMessage.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/coffees`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                description,
                category,
                image_choice: imageChoice
            })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to add coffee');
        }
        
        const newCoffee = await response.json();
        
        // Add to state and close
        coffeesState.push(newCoffee);
        closeModal();
        
        // Show success
        showToast(`${newCoffee.name} has been added!`);
        
        // Refresh view
        renderCoffees();
        updateStats();
        
    } catch (error) {
        console.error('Error adding coffee:', error);
        formErrorMessage.textContent = error.message;
        formErrorMessage.style.display = 'block';
    }
});

// Reset Database Handler
resetDbBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to reset the database? This deletes all custom suggestions and resets vote tallies.')) {
        try {
            const response = await fetch(`${API_URL}/coffees/reset`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Reset failed');
            }
            
            const result = await response.json();
            showToast(result.message);
            fetchCoffees();
        } catch (error) {
            console.error('Error resetting database:', error);
            showToast('Could not reset database.', 'error');
        }
    }
});
