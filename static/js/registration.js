// Multi-step Registration Form Handler
let currentStep = 1;
const totalSteps = 5;

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    setupPasswordStrength();
    setupFileUpload();
    updateFormDisplay();

    // Add event listeners for real-time validation
    setupRealTimeValidation();
});

// Setup Real-time Validation
function setupRealTimeValidation() {
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function () {
            if (this.value && !isValidEmail(this.value)) {
                this.classList.add('error');
            } else {
                this.classList.remove('error');
            }
        });
    }

    const dobInput = document.getElementById('date_of_birth');
    if (dobInput) {
        dobInput.addEventListener('change', function () {
            const age = calculateAge(this.value);
            if (age < 13) {
                this.classList.add('error');
            } else {
                this.classList.remove('error');
            }
        });
    }
}

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

    // Step 1: Personal Information
    if (currentStep === 1) {
        // Validate age
        const dobInput = document.getElementById('date_of_birth');
        if (dobInput.value) {
            const age = calculateAge(dobInput.value);
            if (age < 13) {
                showAlert('You must be at least 13 years old to register', 'error');
                dobInput.classList.add('error');
                isValid = false;
            } else {
                dobInput.classList.remove('error');
            }
        }

        // Check if gender is selected
        const genderSelected = document.querySelector('input[name="gender"]:checked');
        if (!genderSelected) {
            showAlert('Please select your gender', 'error');
            isValid = false;
        }
    }

    // Step 2: Contact Details
    if (currentStep === 2) {
        // Validate email
        const emailInput = document.getElementById('email');
        if (emailInput.value && !isValidEmail(emailInput.value)) {
            showAlert('Please enter a valid email address', 'error');
            emailInput.classList.add('error');
            isValid = false;
        } else {
            emailInput.classList.remove('error');
        }

        // Validate phone
        const phoneInput = document.getElementById('phone');
        if (phoneInput.value && phoneInput.value.length < 10) {
            showAlert('Please enter a valid phone number', 'error');
            phoneInput.classList.add('error');
            isValid = false;
        } else {
            phoneInput.classList.remove('error');
        }
    }

    // Step 3: Interests
    if (currentStep === 3) {
        const checkedInterests = document.querySelectorAll('input[name="interests"]:checked');
        if (checkedInterests.length < 3) {
            showAlert('Please select at least 3 interests', 'error');
            isValid = false;
        }
    }

    // Step 4: Security
    if (currentStep === 4) {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;

        if (password !== confirmPassword) {
            showAlert('Passwords do not match', 'error');
            document.getElementById('confirm_password').classList.add('error');
            isValid = false;
        } else {
            document.getElementById('confirm_password').classList.remove('error');
        }

        if (!isStrongPassword(password)) {
            showAlert('Please create a stronger password that meets all requirements', 'error');
            document.getElementById('password').classList.add('error');
            isValid = false;
        } else {
            document.getElementById('password').classList.remove('error');
        }
    }

    // Check all required fields
    inputs.forEach(input => {
        if (input.type === 'radio') {
            const radioGroup = currentStepElement.querySelector(`input[name="${input.name}"]:checked`);
            if (!radioGroup) {
                isValid = false;
            }
        } else if (input.type === 'checkbox' && input.name !== 'interests' && input.name !== 'terms') {
            if (!input.checked) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        } else if (!input.value) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });

    if (!isValid && currentStep !== 3) {
        showAlert('Please fill in all required fields correctly', 'error');
    }

    return isValid;
}

// Password Strength Checker
function setupPasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;

    passwordInput.addEventListener('input', function () {
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
            strengthFill.style.width = '33%';
            strengthText.textContent = 'Weak password';
        } else if (strength === 2) {
            strengthFill.className = 'strength-fill medium';
            strengthFill.style.width = '66%';
            strengthText.textContent = 'Medium password';
        } else {
            strengthFill.className = 'strength-fill strong';
            strengthFill.style.width = '100%';
            strengthText.textContent = 'Strong password';
        }
    });
}

// File Upload Handler
function setupFileUpload() {
    const fileArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('profile_picture');
    const filePreview = document.getElementById('filePreview');
    const previewImage = document.getElementById('previewImage');
    const fileNameSpan = document.getElementById('fileName');
    const uploadContent = document.querySelector('.upload-content');

    if (fileArea && fileInput) {
        // Click to upload
        fileArea.onclick = () => fileInput.click();

        // File input change handler
        fileInput.onchange = function () {
            const file = this.files[0];
            if (file) {
                // Validate file size (5MB max)
                if (file.size > 5 * 1024 * 1024) {
                    showAlert('File size must be less than 5MB', 'error');
                    this.value = '';
                    return;
                }

                // Validate file type
                if (!file.type.startsWith('image/')) {
                    showAlert('Please upload an image file', 'error');
                    this.value = '';
                    return;
                }

                // Display the file name
                fileNameSpan.textContent = file.name;

                // Show the image preview
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                    filePreview.classList.remove('hidden');
                    uploadContent.classList.add('hidden');
                };
                reader.readAsDataURL(file);
            }
        };

        // Drag and drop support
        fileArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.style.borderColor = '#667eea';
        });

        fileArea.addEventListener('dragleave', function (e) {
            e.preventDefault();
            this.style.borderColor = '';
        });

        fileArea.addEventListener('drop', function (e) {
            e.preventDefault();
            this.style.borderColor = '';

            const file = e.dataTransfer.files[0];
            if (file) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    }
}

// Remove File
function removeFile() {
    const fileInput = document.getElementById('profile_picture');
    const uploadContent = document.querySelector('.upload-content');
    const filePreview = document.getElementById('filePreview');

    fileInput.value = '';
    uploadContent.classList.remove('hidden');
    filePreview.classList.add('hidden');
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

    // Get selected interests
    const interests = Array.from(document.querySelectorAll('input[name="interests"]:checked'))
        .map(cb => {
            const label = cb.parentElement.querySelector('span').textContent.trim();
            return label;
        })
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
            <span>${new Date(dob).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
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

    // Validate interests one more time before submission
    const checkedInterests = document.querySelectorAll('input[name="interests"]:checked');
    if (checkedInterests.length < 3) {
        closeModal('confirmModal');
        showAlert('Please select at least 3 interests', 'error');
        currentStep = 3;
        updateFormDisplay();
        return;
    }

    closeModal('confirmModal');

    // Show loading indicator
    const submitButton = event?.target;
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span>Creating Account...</span>';
    }

    // Submit the form
    const form = document.getElementById('registrationForm');
    form.submit();
}

// Show Success Modal (Called after successful registration)
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

    // Auto-remove after 5 seconds
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
window.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// Prevent form submission on Enter key (except in textareas)
document.getElementById('registrationForm')?.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        return false;
    }
});