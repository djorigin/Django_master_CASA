/**
 * Master JavaScript file for Aviation Management System
 * Handles common functionality across all apps
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize common functionality
    initializeAlerts();
    initializeDropdowns();
    initializeTooltips();
    initializeConfirmActions();
    
});

/**
 * Alert/Message handling
 */
function initializeAlerts() {
    // Auto-hide success messages after 5 seconds
    const successAlerts = document.querySelectorAll('.alert-success');
    successAlerts.forEach(function(alert) {
        setTimeout(function() {
            fadeOutElement(alert);
        }, 5000);
    });
    
    // Handle alert close buttons
    const closeButtons = document.querySelectorAll('.alert .close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            fadeOutElement(this.parentElement);
        });
    });
}

/**
 * Dropdown menu handling
 */
function initializeDropdowns() {
    const dropdownMenus = document.querySelectorAll('.user-menu');
    
    dropdownMenus.forEach(function(menu) {
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.querySelector('.user-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('show');
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        const openDropdowns = document.querySelectorAll('.user-dropdown.show');
        openDropdowns.forEach(function(dropdown) {
            dropdown.classList.remove('show');
        });
    });
}

/**
 * Tooltip initialization (for future use)
 */
function initializeTooltips() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Confirmation dialogs for destructive actions
 */
function initializeConfirmActions() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Smooth fade out animation
 */
function fadeOutElement(element) {
    element.style.transition = 'opacity 0.3s ease';
    element.style.opacity = '0';
    
    setTimeout(function() {
        element.style.display = 'none';
    }, 300);
}

/**
 * Form validation helpers
 */
function validateRequired(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

/**
 * CSRF Token helper for AJAX requests
 */
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

/**
 * Show loading spinner
 */
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        element.disabled = true;
    }
}

/**
 * Hide loading spinner
 */
function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

/**
 * Format numbers with thousand separators
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Debounce function for search inputs
 */
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

// Export functions for use in other scripts
window.AviationJS = {
    fadeOutElement: fadeOutElement,
    validateRequired: validateRequired,
    getCSRFToken: getCSRFToken,
    showLoading: showLoading,
    hideLoading: hideLoading,
    formatNumber: formatNumber,
    debounce: debounce
};