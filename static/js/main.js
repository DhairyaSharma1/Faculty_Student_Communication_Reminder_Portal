// Main JavaScript file for general functionality

// Initialize Bootstrap tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Flash message auto-close
    var flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            var alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000); // Auto-close after 5 seconds
    });
});

// Form validation
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return true;
    
    var isValid = true;
    var requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Date formatting function
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Add event listener to required fields to remove validation styling on input
document.addEventListener('DOMContentLoaded', function() {
    var requiredFields = document.querySelectorAll('[required]');
    requiredFields.forEach(function(field) {
        field.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    });
});

