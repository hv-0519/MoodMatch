// Multi-step Registration Form Handler
let currentStep = 1;
const totalSteps = 5;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupPasswordStrength();
    setupFileUpload();
    updateFormDisplay();
});

// Change Step Function
function changeStep(direction) {
    if (direction === 1 && !validateCurrentStep()) {
        return;
    }

    const newStep = currentStep + direction;
    
    if (newStep >= 1 && newStep <= totalSteps) {
        currentStep = newStep;
        updateFormDisplay();
        
        if (currentStep === totalSteps) {
            populateReview();
        }
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    if (direction === 1 && currentStep === totalSteps) {
        showConfirmModal();
    }
}

// Update Form Display
function updateFormDisplay() {
    // Update steps
    document.querySelectorAll('.form-step').forEach((step, index) => {
        step.classList.toggle('active', index + 1 === currentStep);
    });
    
    // Update progress
    document.querySelectorAll('.progress-steps .step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNum === currentStep) {
            step.classList.add('active');
        } else if (stepNum < currentStep) {
            step.classList.add('completed');
        }
    });
    
    // Update buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    prevBtn.style.display = currentStep === 1 ? 'none' : 'inline-flex';
    
    if (currentStep === totalSteps) {
        nextBtn.style.display = 'none';
    } else {
        nextBtn.style.display = 'inline-flex';
        nextBtn.querySelector('span').textContent = 'Continue';
    }
}

// Validate Current Step
function validateCurrentStep() {
    const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    const inputs = currentStepElement.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    if (currentStep === 1) {
        // Validate age
        const dobInput = document.getElementById('date_of_birth');
        if (dobInput.value) {
            const age = calculateAge(dobInput.value);
            if (age < 13) {
                showAlert('You must be at least 13 years old to register', 'error');
                isValid = false;
            }
        }
    }
    
    if (currentStep === 2) {
        // Validate email
        const emailInput = document.getElementById('email');
        if (emailInput.value && !isValidEmail(emailInput.value)) {
            showAlert('Please enter a valid email address', 'error');
            isValid = false;
        }
    }
    
    if (currentStep === 3) {
        // Validate interests
        const checkedInterests = document.querySelectorAll('input[name="interests"]:checked');
        if (checkedInterests.length < 3) {
            showAlert('Please select at least 3 interests', 'error');
            isValid = false;
        }
    }
    
    if (currentStep === 4) {
        // Validate password strength
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        if (password !== confirmPassword) {
            showAlert('Passwords do not match', 'error');
            isValid = false;
        }
        
        if (!isStrongPassword(password)) {
            showAlert('Please create a stronger password that meets all requirements', 'error');
            isValid = false;
        }
    }
    
    // Check all required fields
    inputs.forEach(input => {
        if (!input.value || (input.type === 'radio' && !currentStepElement.querySelector(`input[name="${input.name}"]:checked`))) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// Password Strength Checker
function setupPasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;
    
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const strengthFill = document.getElementById('strengthFill');
        const strengthText = document.getElementById('strengthText');
        
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            number: /[0-9]/.test(password)
        };
        
        // Update requirement indicators
        document.getElementById('req-length').classList.toggle('met', requirements.length);
        document.getElementById('req-uppercase').classList.toggle('met', requirements.uppercase);
        document.getElementById('req-number').classList.toggle('met', requirements.number);
        
        // Calculate strength
        const strength = Object.values(requirements).filter(Boolean).length;
        
        if (strength === 0) {
            strengthFill.className = 'strength-fill';
            strengthFill.style.width = '0%';
            strengthText.textContent = 'Password strength';
        } else if (strength === 1) {
            strengthFill.className = 'strength-fill weak';
            strengthText.textContent = 'Weak password';
        } else if (strength === 2) {
            strengthFill.className = 'strength-fill medium';
            strengthText.textContent = 'Medium password';
        } else {
            strengthFill.className = 'strength-fill strong';
            strengthText.textContent = 'Strong password';
        }
    });
}

// File Upload Handler
function setupFileUpload() {
    const fileInput = document.getElementById('profile_picture');
    const uploadArea = document.getElementById('fileUploadArea');
    const preview = document.getElementById('filePreview');
    
    if (!fileInput || !uploadArea) return;
    
    fileInput.addEventListener('change', function(e) {
        handleFileSelect(e.target.files[0]);
    });
    
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#667eea';
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '';
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect(file);
        }
    });
}

function handleFileSelect(file) {
    if (!file) return;
    
    if (file.size > 5 * 1024 * 1024) {
        showAlert('File size must be less than 5MB', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('fileName').textContent = file.name;
        document.querySelector('.upload-content').style.display = 'none';
        document.getElementById('filePreview').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function removeFile() {
    document.getElementById('profile_picture').value = '';
    document.querySelector('.upload-content').style.display = 'block';
    document.getElementById('filePreview').classList.add('hidden');
}

// Toggle Password Visibility
function togglePasswordField(fieldId) {
    const input = document.getElementById(fieldId);
    const button = input.parentElement.querySelector('.password-toggle');
    const eyeOpen = button.querySelector('.eye-open');
    const eyeClosed = button.querySelector('.eye-closed');
    
    if (input.type === 'password') {
        input.type = 'text';
        eyeOpen.classList.add('hidden');
        eyeClosed.classList.remove('hidden');
    } else {
        input.type = 'password';
        eyeOpen.classList.remove('hidden');
        eyeClosed.classList.add('hidden');
    }
}

// Populate Review Section
function populateReview() {
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const gender = document.querySelector('input[name="gender"]:checked')?.value || '';
    const dob = document.getElementById('date_of_birth').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const street = document.getElementById('street').value;
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const postalCode = document.getElementById('postal_code').value;
    const country = document.getElementById('country');
    const countryText = country.options[country.selectedIndex]?.text || '';
    
    const interests = Array.from(document.querySelectorAll('input[name="interests"]:checked'))
        .map(cb => cb.value)
        .join(', ');
    
    const reviewHtml = `
        <div class="review-item">
            <strong>Name:</strong>
            <span>${firstName} ${lastName}</span>
        </div>
        <div class="review-item">
            <strong>Gender:</strong>
            <span>${gender.charAt(0).toUpperCase() + gender.slice(1)}</span>
        </div>
        <div class="review-item">
            <strong>Date of Birth:</strong>
            <span>${new Date(dob).toLocaleDateString()}</span>
        </div>
        <div class="review-item">
            <strong>Email:</strong>
            <span>${email}</span>
        </div>
        <div class="review-item">
            <strong>Phone:</strong>
            <span>${phone}</span>
        </div>
        <div class="review-item">
            <strong>Address:</strong>
            <span>${street}, ${city}, ${state} ${postalCode}, ${countryText}</span>
        </div>
        <div class="review-item">
            <strong>Interests:</strong>
            <span>${interests || 'None selected'}</span>
        </div>
    `;
    
    document.getElementById('reviewContent').innerHTML = reviewHtml;
}

// Show Confirmation Modal
function showConfirmModal() {
    const modal = document.getElementById('confirmModal');
    modal.classList.add('active');
}

// Close Modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
}

// Submit Form
function submitForm() {
    const termsCheckbox = document.getElementById('terms');
    if (!termsCheckbox.checked) {
        closeModal('confirmModal');
        showAlert('You must accept the terms and conditions', 'error');
        return;
    }
    
    closeModal('confirmModal');
    
    // Submit the actual form
    const form = document.getElementById('registrationForm');
    form.submit();
    
    // Show success modal (in real app, this would be after server confirmation)
    setTimeout(() => {
        showSuccessModal();
    }, 500);
}

// Show Success Modal
function showSuccessModal() {
    const modal = document.getElementById('successModal');
    modal.classList.add('active');
    
    // Redirect after 2 seconds
    setTimeout(() => {
        window.location.href = '/login';
    }, 2000);
}

// Show Alert
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        ${message}
    `;
    
    const formHeader = document.querySelector('.form-header');
    const existingAlert = formHeader.nextElementSibling;
    if (existingAlert && existingAlert.classList.contains('alert')) {
        existingAlert.remove();
    }
    formHeader.after(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

// Helper Functions
function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isStrongPassword(password) {
    return password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password);
}

// Close modal when clicking outside
window.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});