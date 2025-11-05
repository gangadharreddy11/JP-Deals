// Sample deals data (fallback if no data from server)
const dealsData = [];

let currentDeals = [...dealsData];
let currentCategory = 'all';

// Load deals on page load (DISABLED - using Flask server-rendered content)
function loadDeals() {
    // This function is disabled to preserve Flask server-rendered content
    // The grid is already populated by Flask templates
    console.log('loadDeals() called but disabled to preserve server-rendered content');
    return;
}

// Create deal card HTML
function createDealCard(deal) {
    return `
        <div class="deal-card" data-category="${deal.category}">
            <img src="${deal.image}" alt="${deal.title}" class="deal-image">
            <div class="deal-content">
                <div class="deal-title">${deal.title}</div>
                <div class="deal-meta">
                    <div class="deal-price">
                        <span class="price-now">₹${deal.price.toLocaleString()}</span>
                        <span class="price-was">₹${deal.originalPrice.toLocaleString()}</span>
                    </div>
                    <span class="discount-badge">${deal.discount}% OFF</span>
                </div>
                <div class="deal-footer">
                    <span class="category-tag">${getCategoryName(deal.category)}</span>
                    <button class="wishlist-btn" onclick="toggleWishlist(${deal.id}, event)">🤍</button>
                </div>
                <button class="btn-buy" onclick="trackClick(${deal.id}, '${deal.affiliate}')">Buy Now</button>
            </div>
        </div>
    `;
}

// Get category display name
function getCategoryName(slug) {
    const names = {
        electronics: '📱 Electronics',
        fashion: '👕 Fashion',
        home: '🏠 Home',
        beauty: '💄 Beauty',
        books: '📚 Books',
        sports: '⚽ Sports'
    };
    return names[slug] || slug;
}

// Filter by category
function filterByCategory(category) {
    currentCategory = category;
    
    // Update active state
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.remove('active');
    });
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // For Flask backend, redirect to category page or reload with filter
    if (category === 'all') {
        window.location.href = '/';
    } else {
        window.location.href = '/category/' + category;
    }
}

// Sort deals
function sortDeals(sortBy) {
    // For now, just reload the page with the sort parameter
    const url = new URL(window.location);
    url.searchParams.set('sort', sortBy);
    window.location.href = url.toString();
}

// Filter by price
function filterByPrice(maxPrice) {
    // For now, just reload the page with the price filter parameter
    const url = new URL(window.location);
    if (maxPrice === 'all') {
        url.searchParams.delete('max_price');
    } else {
        url.searchParams.set('max_price', maxPrice);
    }
    window.location.href = url.toString();
}

// Search deals
function searchDeals() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const query = searchInput.value.trim();
    if (query) {
        const url = new URL(window.location);
        url.searchParams.set('search', query);
        window.location.href = url.toString();
    }
}

// Track click (redirect to affiliate link)
function trackClick(dealId, affiliateUrl, event) {
    if (affiliateUrl) {
        // Show brief feedback
        const button = event ? event.target : null;
        if (button) {
            const originalText = button.textContent;
            button.textContent = 'Redirecting...';
            button.disabled = true;
        
            // Reset button after a short delay
            setTimeout(() => {
                button.textContent = originalText;
                button.disabled = false;
            }, 1000);
        }
        
        // Open affiliate link in new tab
        window.open(affiliateUrl, '_blank');
        
        // Log the click for analytics
        console.log(`Click tracked for deal ID: ${dealId}, URL: ${affiliateUrl}`);
        
        // In production, you would send this to your analytics service
        // fetch('/api/track-click', {
        //     method: 'POST',
        //     headers: {'Content-Type': 'application/json'},
        //     body: JSON.stringify({dealId: dealId, url: affiliateUrl})
        // });
    } else {
        alert(`Redirecting to affiliate link for deal #${dealId}...\n\nIn production, this would:\n1. Log the click to database\n2. Redirect to the actual affiliate URL`);
    }
}

// Toggle wishlist
function toggleWishlist(dealId, event) {
    if (event) {
        event.stopPropagation();
    }
    const btn = event.target;
    btn.classList.toggle('active');
    btn.textContent = btn.classList.contains('active') ? '❤️' : '🤍';
    
    // In production, save to localStorage or database
    console.log(`Wishlist toggled for deal ID: ${dealId}`);
}

// Admin functionality
function confirmDelete(message = 'Are you sure you want to delete this item? This action cannot be undone.') {
    return confirm(message);
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
    `;
    
    if (type === 'success') {
        notification.style.background = '#28a745';
    } else if (type === 'error') {
        notification.style.background = '#dc3545';
    } else {
        notification.style.background = '#17a2b8';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Enhanced form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#dc3545';
            isValid = false;
        } else {
            field.style.borderColor = '#ddd';
        }
    });
    
    if (!isValid) {
        showNotification('Please fill in all required fields', 'error');
    }
    
    return isValid;
}

// Auto-save form data to localStorage
function autoSaveForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        const key = `${formId}_${input.name}`;
        
        // Load saved value
        const savedValue = localStorage.getItem(key);
        if (savedValue && !input.value) {
            input.value = savedValue;
        }
        
        // Save on change
        input.addEventListener('input', () => {
            localStorage.setItem(key, input.value);
        });
    });
}

// Clear form data from localStorage
function clearFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        const key = `${formId}_${input.name}`;
        localStorage.removeItem(key);
    });
}

// Allow search on Enter key
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchDeals();
            }
        });
    }
    
    // Auto-save forms
    autoSaveForm('categoryForm');
    autoSaveForm('productForm');
    autoSaveForm('dealForm');
    
    // Note: loadDeals() removed to preserve Flask server-rendered content
    console.log('Page loaded - using Flask server-rendered content');
});
