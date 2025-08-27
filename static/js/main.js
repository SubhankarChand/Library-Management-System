// JavaScript for Library Management System

document.addEventListener('DOMContentLoaded', function() {
    // Toggle book description
    document.querySelectorAll('.toggle-details').forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            const shortDesc = document.querySelector(`.description-short[data-book="${bookId}"]`);
            const fullDesc = document.querySelector(`.description-full[data-book="${bookId}"]`);
            const icon = this.querySelector('i');
            
            if (shortDesc && fullDesc) {
                if (shortDesc.style.display === 'none') {
                    shortDesc.style.display = 'block';
                    fullDesc.style.display = 'none';
                    icon.className = 'fas fa-chevron-down';
                    this.innerHTML = '<i class="fas fa-chevron-down"></i> View more details';
                } else {
                    shortDesc.style.display = 'none';
                    fullDesc.style.display = 'block';
                    icon.className = 'fas fa-chevron-up';
                    this.innerHTML = '<i class="fas fa-chevron-up"></i> View less';
                }
            }
        });
    });
    
    // Auto-submit filter form when dropdowns change
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        document.getElementById('categoryFilter')?.addEventListener('change', () => filterForm.submit());
        document.getElementById('typeFilter')?.addEventListener('change', () => filterForm.submit());
        document.getElementById('statusFilter')?.addEventListener('change', () => filterForm.submit());
    }
    
    // Clear search functionality
    window.clearSearch = function() {
        document.getElementById('searchInput').value = '';
        filterForm.submit();
    }
    
    // Password confirmation validation
    const registerForm = document.querySelector('form[action="{{ url_for(\'register\') }}"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match!');
                confirmPassword.focus();
            }
        });
    }
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Publisher registration fields toggle
    const roleRadios = document.querySelectorAll('input[name="role"]');
    const publisherFields = document.getElementById('publisherFields');
    
    if (roleRadios.length && publisherFields) {
        roleRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'publisher') {
                    publisherFields.style.display = 'block';
                } else {
                    publisherFields.style.display = 'none';
                }
            });
        });
    }
    
    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });
});