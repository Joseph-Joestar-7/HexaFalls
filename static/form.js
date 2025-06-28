// Form data object
let formData = {
    name: '',
    category: '',
    class: '',
    semester: '',
    exam: '',
    subjects: ''
};

// Error tracking
let errors = {};

// Theme toggle functionality
function initializeTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Add click event listener
    themeToggle.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Initialize the form and theme
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    
    const form = document.getElementById('educationForm');
    form.addEventListener('submit', handleSubmit);
    
    // Add input event listeners for real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('input', () => clearError(input.name));
        input.addEventListener('change', () => clearError(input.name));
    });
});

// Handle category change
function handleCategoryChange() {
    const category = document.getElementById('category').value;
    
    // Reset form data for conditional fields
    formData = {
        name: formData.name,
        category: category,
        class: '',
        semester: '',
        exam: '',
        subjects: category === 'competitive' ? '' : formData.subjects
    };
    
    // Clear all errors
    errors = {};
    clearAllErrors();
    
    // Hide all conditional fields
    hideAllConditionalFields();
    
    // Show relevant fields based on category
    if (category === 'school') {
        showField('schoolFields');
        showField('subjectsField');
    } else if (category === 'college') {
        showField('collegeFields');
        showField('subjectsField');
    } else if (category === 'competitive') {
        showField('competitiveFields');
    } else {
        showField('subjectsField');
    }
}

// Show a conditional field with animation
function showField(fieldId) {
    const field = document.getElementById(fieldId);
    field.style.display = 'block';
    // Trigger animation
    setTimeout(() => {
        field.classList.add('show');
    }, 10);
}

// Hide all conditional fields
function hideAllConditionalFields() {
    const fields = ['schoolFields', 'collegeFields', 'competitiveFields', 'subjectsField'];
    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        field.classList.remove('show');
        field.style.display = 'none';
    });
}

// Validate form
function validateForm() {
    const newErrors = {};
    
    // Get current form values
    const name = document.getElementById('name').value.trim();
    const category = document.getElementById('category').value;
    const classValue = document.getElementById('class').value;
    const semester = document.getElementById('semester').value;
    const exam = document.getElementById('exam').value;
    const subjects = document.getElementById('subjects').value.trim();
    
    // Validate name
    if (!name) {
        newErrors.name = 'Name is required';
    }
    
    // Validate category
    if (!category) {
        newErrors.category = 'Category is required';
    }
    
    // Validate conditional fields
    if (category === 'school' && !classValue) {
        newErrors.class = 'Class is required';
    }
    
    if (category === 'college' && !semester) {
        newErrors.semester = 'Semester is required';
    }
    
    if (category === 'competitive' && !exam) {
        newErrors.exam = 'Exam is required';
    }
    
    if (category !== 'competitive' && !subjects) {
        newErrors.subjects = 'Subjects are required';
    }
    
    errors = newErrors;
    return Object.keys(newErrors).length === 0;
}

// Display errors
function displayErrors() {
    // Clear previous errors
    clearAllErrors();
    
    // Display new errors
    Object.keys(errors).forEach(field => {
        const errorElement = document.getElementById(field + 'Error');
        const inputElement = document.getElementById(field);
        
        if (errorElement && inputElement) {
            errorElement.textContent = errors[field];
            inputElement.classList.add('error');
        }
    });
}

// Clear specific error
function clearError(fieldName) {
    if (errors[fieldName]) {
        delete errors[fieldName];
        const errorElement = document.getElementById(fieldName + 'Error');
        const inputElement = document.getElementById(fieldName);
        
        if (errorElement) {
            errorElement.textContent = '';
        }
        if (inputElement) {
            inputElement.classList.remove('error');
        }
    }
}

// Clear all errors
function clearAllErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    const inputElements = document.querySelectorAll('input.error, select.error');
    
    errorElements.forEach(element => {
        element.textContent = '';
    });
    
    inputElements.forEach(element => {
        element.classList.remove('error');
    });
}

// Handle form submission
function handleSubmit(event) {
    event.preventDefault();
    
    if (validateForm()) {
        // Get form data
        const name = document.getElementById('name').value.trim();
        const category = document.getElementById('category').value;
        const classValue = document.getElementById('class').value;
        const semester = document.getElementById('semester').value;
        const exam = document.getElementById('exam').value;
        const subjects = document.getElementById('subjects').value.trim();
        
        // Update form data object
        formData = {
            name,
            category,
            class: classValue || undefined,
            semester: semester || undefined,
            exam: exam || undefined,
            subjects
        };
        
        console.log('Form submitted:', formData);
        
        // Show success toast
        showToast('Form Submitted Successfully!', `Welcome ${name}! Your educational profile has been saved.`, 'success');
        
        // Reset form
        resetForm();
    } else {
        // Display errors
        displayErrors();
        
        // Show error toast
        showToast('Please fix the errors', 'Check the form and fill in all required fields.', 'error');
    }
}

// Reset form
function resetForm() {
    document.getElementById('educationForm').reset();
    formData = {
        name: '',
        category: '',
        class: '',
        semester: '',
        exam: '',
        subjects: ''
    };
    errors = {};
    clearAllErrors();
    hideAllConditionalFields();
}

// Show toast notification
function showToast(title, message, type = 'success') {
    const toast = document.getElementById('toast');
    
    toast.innerHTML = `
        <h4>${title}</h4>
        <p>${message}</p>
    `;
    
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    // Hide toast after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}
