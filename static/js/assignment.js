document.addEventListener('DOMContentLoaded', function() {
    // Handle assignment status display
    const updateAssignmentStatus = () => {
        const assignmentCards = document.querySelectorAll('.assignment-card');
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        assignmentCards.forEach(card => {
            const dueDateElem = card.querySelector('[data-due-date]');
            if (!dueDateElem) return;
            
            const dueDate = new Date(dueDateElem.dataset.dueDate);
            dueDate.setHours(0, 0, 0, 0);
            
            const daysDiff = Math.round((dueDate - today) / (1000 * 60 * 60 * 24));
            
            // Remove any existing status classes
            card.classList.remove('overdue', 'due-soon');
            
            // Add appropriate status class
            if (daysDiff < 0) {
                card.classList.add('overdue');
                dueDateElem.innerHTML = 'Overdue! <span class="badge bg-danger">Past Due</span>';
            } else if (daysDiff <= 2) {
                card.classList.add('due-soon');
                dueDateElem.innerHTML = `Due Soon <span class="badge bg-warning text-dark">${daysDiff} day${daysDiff !== 1 ? 's' : ''} left</span>`;
            }
        });
    };
    
    // Initialize status display
    updateAssignmentStatus();
    
    // Handle delete modal
    const deleteModal = document.getElementById('deleteModal');
    
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const title = button.getAttribute('data-title');
            const id = button.getAttribute('data-id');
    
            const modalTitleEl = deleteModal.querySelector('#modalAssignmentTitle');
            const deleteForm = deleteModal.querySelector('#deleteForm');
    
            modalTitleEl.textContent = title;
            
            // Updated line to use the correct URL pattern
            const deleteUrl = deleteForm.getAttribute('data-url-pattern').replace('0', id);
            deleteForm.setAttribute('action', deleteUrl);
        });
    }
    
    // Form validation for assignment form
    const assignmentForm = document.getElementById('assignmentForm');
    if (assignmentForm) {
        assignmentForm.addEventListener('submit', function(e) {
            if (!validateForm('assignmentForm')) {
                e.preventDefault();
                const alert = document.createElement('div');
                alert.className = 'alert alert-danger mt-3';
                alert.textContent = 'Please fill out all required fields';
                assignmentForm.parentNode.insertBefore(alert, assignmentForm.nextSibling);
                setTimeout(() => alert.remove(), 5000);
            }
        });
    }
    
    // Section filter functionality
    const sectionFilter = document.getElementById('sectionFilter');
    if (sectionFilter) {
        sectionFilter.addEventListener('change', function() {
            const selectedSection = this.value;
            const assignmentRows = document.querySelectorAll('[data-section]');
            
            assignmentRows.forEach(row => {
                if (selectedSection === 'all' || row.dataset.section === selectedSection) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});

// Helper function for form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}