// RentAssured - Main JavaScript

// Global variables
let currentUser = null;
let cartItems = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    loadUserData();
    updateNavigation();
    initializeSearch();
    initializeCart();
});

// Load user data from localStorage
function loadUserData() {
    const userData = localStorage.getItem('user');
    if (userData) {
        try {
            currentUser = JSON.parse(userData);
        } catch (e) {
            console.error('Error parsing user data:', e);
            currentUser = null;
        }
    }
}

// Check if user is authenticated
function isAuthenticated() {
    return currentUser !== null && localStorage.getItem('access_token') !== null;
}

// Get authentication token
function getAuthToken() {
    return localStorage.getItem('access_token');
}

// Update navigation based on authentication status
function updateNavigation() {
    const guestNav = document.getElementById('nav-guest-login');
    const userNav = document.getElementById('nav-user-menu');
    const createListingLink = document.getElementById('nav-create-listing');
    const dashboardLink = document.getElementById('nav-dashboard');
    const userName = document.getElementById('user-name');
    
    if (isAuthenticated()) {
        // Show user navigation
        if (guestNav) guestNav.classList.add('d-none');
        if (userNav) userNav.classList.remove('d-none');
        if (userName && currentUser) userName.textContent = currentUser.name;
        
        // Add token to protected links
        const token = getAuthToken();
        if (createListingLink) {
            createListingLink.href = `/create_listing?token=${token}`;
        }
        if (dashboardLink) {
            dashboardLink.href = `/dashboard?token=${token}`;
        }
    } else {
        // Show guest navigation
        if (guestNav) guestNav.classList.remove('d-none');
        if (userNav) userNav.classList.add('d-none');
    }
}

// Initialize search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('#globalSearch, #mobileSearch');
    
    searchInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch(this.value);
            }
        });
    });
}

// Perform search
function performSearch(query) {
    if (query.trim()) {
        window.location.href = `/listings?search=${encodeURIComponent(query.trim())}`;
    }
}

// Initialize cart functionality
function initializeCart() {
    loadCartItems();
    updateCartCount();
}

// Load cart items from localStorage
function loadCartItems() {
    const cartData = localStorage.getItem('cart');
    if (cartData) {
        try {
            cartItems = JSON.parse(cartData);
        } catch (e) {
            console.error('Error parsing cart data:', e);
            cartItems = [];
        }
    }
}

// Save cart items to localStorage
function saveCartItems() {
    localStorage.setItem('cart', JSON.stringify(cartItems));
}

// Update cart count display
function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.textContent = cartItems.length;
    }
}

// Add item to cart
function addToCart(listingId, title, price) {
    if (!isAuthenticated()) {
        alert('Please login to add items to cart');
        window.location.href = '/login';
        return;
    }
    
    const existingItem = cartItems.find(item => item.id === listingId);
    if (!existingItem) {
        cartItems.push({
            id: listingId,
            title: title,
            price: price,
            addedAt: new Date().toISOString()
        });
        saveCartItems();
        updateCartCount();
        
        // Show success message
        showNotification('Item added to cart!', 'success');
    } else {
        showNotification('Item already in cart!', 'warning');
    }
}

// Remove item from cart
function removeFromCart(listingId) {
    cartItems = cartItems.filter(item => item.id !== listingId);
    saveCartItems();
    updateCartCount();
    showNotification('Item removed from cart!', 'info');
}

// Toggle cart visibility
function toggleCart() {
    // This would open a cart modal or sidebar
    showNotification('Cart functionality coming soon!', 'info');
}

// Go to dashboard
function goToDashboard() {
    if (isAuthenticated()) {
        const token = getAuthToken();
        window.location.href = `/dashboard?token=${token}`;
    } else {
        window.location.href = '/login';
    }
}

// Go to create listing
function goToCreateListing() {
    if (isAuthenticated()) {
        const token = getAuthToken();
        window.location.href = `/create_listing?token=${token}`;
    } else {
        alert('Please login to create a listing');
        window.location.href = '/login';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('cart');
    currentUser = null;
    cartItems = [];
    updateNavigation();
    updateCartCount();
    window.location.href = '/';
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Toggle like functionality
function toggleLike(listingId) {
    if (!isAuthenticated()) {
        alert('Please login to like listings');
        window.location.href = '/login';
        return;
    }
    
    const likeBtn = event.target.closest('.like-btn');
    const icon = likeBtn.querySelector('i');
    
    if (icon.classList.contains('far')) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        likeBtn.classList.add('liked');
        showNotification('Added to favorites!', 'success');
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        likeBtn.classList.remove('liked');
        showNotification('Removed from favorites!', 'info');
    }
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/\s/g, ''));
}

// Show form error
function showFormError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    // Remove existing error
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message text-danger small mt-1';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
    field.classList.add('is-invalid');
}

// Clear form errors
function clearFormErrors() {
    document.querySelectorAll('.error-message').forEach(el => el.remove());
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Lazy loading for images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading when DOM is ready
document.addEventListener('DOMContentLoaded', initializeLazyLoading);

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // Page became visible, refresh user data
        loadUserData();
        updateNavigation();
    }
});

// Handle storage changes (for multi-tab sync)
window.addEventListener('storage', function(e) {
    if (e.key === 'access_token' || e.key === 'user') {
        loadUserData();
        updateNavigation();
    } else if (e.key === 'cart') {
        loadCartItems();
        updateCartCount();
    }
});

// Export functions for global use
window.RentAssured = {
    addToCart,
    removeFromCart,
    toggleLike,
    goToDashboard,
    goToCreateListing,
    logout,
    showNotification,
    isAuthenticated,
    getAuthToken
};