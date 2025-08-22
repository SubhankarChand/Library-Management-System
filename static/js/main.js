// Main JavaScript file for Library Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize interactive elements
    initializeInteractiveElements();
    
    // Auto-dismiss alerts
    autoDismissAlerts();
    
    // Search functionality
    initializeSearch();
    
    // Initialize filter functionality
    initializeFilters();
    
    // Initialize expandable details
    initializeExpandableDetails();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Get all forms with validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation for specific fields
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', validateEmail);
    });
    
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', validatePassword);
    });
}

/**
 * Validate email format
 */
function validateEmail(event) {
    const email = event.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        event.target.setCustomValidity('Please enter a valid email address');
        event.target.classList.add('is-invalid');
    } else {
        event.target.setCustomValidity('');
        event.target.classList.remove('is-invalid');
        if (email) {
            event.target.classList.add('is-valid');
        }
    }
}

/**
 * Validate password strength
 */
function validatePassword(event) {
    const password = event.target.value;
    const minLength = 6;
    
    if (password.length > 0 && password.length < minLength) {
        event.target.setCustomValidity(`Password must be at least ${minLength} characters long`);
        event.target.classList.add('is-invalid');
    } else {
        event.target.setCustomValidity('');
        event.target.classList.remove('is-invalid');
        if (password.length >= minLength) {
            event.target.classList.add('is-valid');
        }
    }
}

/**
 * Initialize interactive elements
 */
function initializeInteractiveElements() {
    // Confirmation dialogs for destructive actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
    
    // Loading states for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Add spinner
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                
                // Restore button state after 5 seconds (fallback)
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    });
    
    // Card hover effects
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInputs = document.querySelectorAll('[data-search-target]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const targetSelector = this.getAttribute('data-search-target');
            const targets = document.querySelectorAll(targetSelector);
            
            targets.forEach(target => {
                const text = target.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    target.style.display = '';
                } else {
                    target.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Initialize dynamic filtering
 */
function initializeFilters() {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) return;
    
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    // Auto-submit form on filter changes with debouncing
    let debounceTimer;
    
    function submitFilters() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            filterForm.submit();
        }, 300);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', submitFilters);
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', () => {
            filterForm.submit();
        });
    }
    
    if (typeFilter) {
        typeFilter.addEventListener('change', () => {
            filterForm.submit();
        });
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            filterForm.submit();
        });
    }
}

/**
 * Initialize expandable book details
 */
function initializeExpandableDetails() {
    const toggleButtons = document.querySelectorAll('.toggle-details');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            const card = this.closest('.book-card');
            const shortDesc = card.querySelector('.description-short');
            const fullDesc = card.querySelector('.description-full');
            const icon = this.querySelector('i');
            const buttonText = this.querySelector('.btn-text') || this;
            
            if (fullDesc.style.display === 'none' || !fullDesc.style.display) {
                // Expand
                shortDesc.style.display = 'none';
                fullDesc.style.display = 'block';
                icon.className = 'fas fa-chevron-up';
                if (this.querySelector('.btn-text')) {
                    this.querySelector('.btn-text').textContent = ' View less details';
                } else {
                    this.innerHTML = '<i class="fas fa-chevron-up"></i> View less details';
                }
                this.classList.add('expanded');
            } else {
                // Collapse
                shortDesc.style.display = 'block';
                fullDesc.style.display = 'none';
                icon.className = 'fas fa-chevron-down';
                if (this.querySelector('.btn-text')) {
                    this.querySelector('.btn-text').textContent = ' View more details';
                } else {
                    this.innerHTML = '<i class="fas fa-chevron-down"></i> View more details';
                }
                this.classList.remove('expanded');
            }
        });
    });
}

/**
 * Clear search input and reload page
 */
function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = '';
        const form = document.getElementById('filterForm');
        if (form) {
            form.submit();
        }
    }
}

/**
 * Show loading state for pagination links
 */
function showPaginationLoading(link) {
    const originalContent = link.innerHTML;
    link.innerHTML = '<span class="loading-spinner"></span> Loading...';
    link.style.pointerEvents = 'none';
    
    // Restore after 5 seconds (fallback)
    setTimeout(() => {
        link.innerHTML = originalContent;
        link.style.pointerEvents = 'auto';
    }, 5000);
}

// Add loading states to pagination links
document.addEventListener('DOMContentLoaded', function() {
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (!this.closest('.page-item').classList.contains('active')) {
                showPaginationLoading(this);
            }
        });
    });
});

/**
 * Utility function to format dates
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Utility function to show toast notifications
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

/**
 * Handle AJAX form submissions
 */
function submitFormAjax(form, successCallback, errorCallback) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok');
    })
    .then(data => {
        if (successCallback) {
            successCallback(data);
        }
    })
    .catch(error => {
        if (errorCallback) {
            errorCallback(error);
        } else {
            showToast('An error occurred. Please try again.', 'danger');
        }
    });
}

/**
 * Smooth scroll to element
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        showToast('Could not copy text', 'danger');
    });
}

// Export functions for use in other scripts
window.LibraryApp = {
    showToast,
    submitFormAjax,
    scrollToElement,
    copyToClipboard,
    formatDate,
    clearSearch,
    initializeFilters,
    initializeExpandableDetails
};
