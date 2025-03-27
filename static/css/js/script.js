// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // ======================
    // Registration Form Logic
    // ======================
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirmPassword');
            
            // Basic validation
            if (!password.value) {
                e.preventDefault();
                showError(password, 'Password is required');
                return;
            }
            
            if (password.value.length < 8) {
                e.preventDefault();
                showError(password, 'Password must be at least 8 characters');
                return;
            }
            
            if (confirmPassword && password.value !== confirmPassword.value) {
                e.preventDefault();
                showError(confirmPassword, 'Passwords do not match');
                return;
            }
        });
    }

    // =================
    // Login Form Logic
    // =================
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            
            if (!email.value || !password.value) {
                e.preventDefault();
                if (!email.value) showError(email, 'Email is required');
                if (!password.value) showError(password, 'Password is required');
            }
        });
    }

    // ======================
    // Course Selection Logic
    // ======================
    const courseForm = document.getElementById('courseForm');
    if (courseForm) {
        // Enable/disable assessment button based on selection
        const courseSelect = document.getElementById('course');
        const levelSelect = document.getElementById('level');
        const assessBtn = document.getElementById('assessBtn');
        
        function updateButtonState() {
            assessBtn.disabled = !courseSelect.value || !levelSelect.value;
        }
        
        courseSelect.addEventListener('change', updateButtonState);
        levelSelect.addEventListener('change', updateButtonState);
        updateButtonState(); // Initial state
    }

    // ========================
    // Assessment Form Logic
    // ========================
    const assessForm = document.getElementById('assessForm');
    if (assessForm) {
        // Range input feedback
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => {
            const valueDisplay = document.getElementById(`${input.id}Value`);
            if (valueDisplay) {
                input.addEventListener('input', () => {
                    valueDisplay.textContent = input.value;
                });
            }
        });

        // Form validation
        assessForm.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredInputs = assessForm.querySelectorAll('[required]');
            
            requiredInputs.forEach(input => {
                if (!input.value) {
                    showError(input, 'This field is required');
                    isValid = false;
                } else if (input.type === 'number') {
                    const min = input.min ? parseInt(input.min) : null;
                    const max = input.max ? parseInt(input.max) : null;
                    
                    if ((min !== null && parseInt(input.value) < min) ||
                        (max !== null && parseInt(input.value) > max)) {
                        showError(input, `Value must be between ${min} and ${max}`);
                        isValid = false;
                    }
                }
            });
            
            if (!isValid) e.preventDefault();
        });
    }

    // ===================
    // Helper Functions
    // ===================
    function showError(input, message) {
        const formGroup = input.closest('.mb-3') || input.closest('.form-group');
        if (!formGroup) return;
        
        // Remove existing errors
        const existingError = formGroup.querySelector('.invalid-feedback');
        if (existingError) existingError.remove();
        
        // Add error class
        input.classList.add('is-invalid');
        
        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        formGroup.appendChild(errorDiv);
        
        // Focus on the problematic field
        input.focus();
    }

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.classList.add('fade');
            setTimeout(() => msg.remove(), 150);
        }, 5000);
    });
});
