// Modern JavaScript for Content Generator AI

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    initializeForm();
    initializeFileUpload();
    initializeScheduleToggle();
    initializeFlashMessages();
    initializeCopyButtons();
});

// Form handling and submission
function initializeForm() {
    const form = document.getElementById('contentForm');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        showLoadingState();
        simulateProgress();

        try {
            // Construct JSON payload from form data
            const formData = new FormData(form);
            const topic = formData.get('topic');
            const platforms = formData.getAll('platforms');
            const scheduleOption = formData.get('schedule_option');
            const scheduleTime = formData.get('schedule_time');

            const payload = {
                topic: topic,
                platforms: platforms,
                schedule_time: scheduleOption === 'later' ? scheduleTime : null
            };

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                displayResults(result.caption, result.content, result.image_url);
            } else {
                throw new Error(result.error || 'Failed to generate content');
            }
        } catch (error) {
            showError(error.message || 'An unexpected error occurred. Please try again.');
        } finally {
            hideLoadingState();
        }
    });
}

// Form validation
function validateForm() {
    const topic = document.getElementById('topic').value.trim();
    const platforms = document.querySelectorAll('input[name="platforms"]:checked');
    
    if (!topic) {
        showError('Please enter a topic for your content.');
        return false;
    }

    if (platforms.length === 0) {
        showError('Please select at least one platform.');
        return false;
    }

    return true;
}

// File upload handling
function initializeFileUpload() {
    const fileInput = document.getElementById('image');
    const fileDisplay = document.querySelector('.file-upload-display');
    const fileText = document.querySelector('.file-text');
    const fileSubtext = document.querySelector('.file-subtext');

    if (!fileInput || !fileDisplay) return;

    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileText.textContent = file.name;
            fileSubtext.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
            fileDisplay.style.borderColor = 'var(--primary-color)';
            fileDisplay.style.background = 'rgba(99, 102, 241, 0.05)';
        } else {
            resetFileUpload();
        }
    });

    // Handle drag and drop
    fileDisplay.addEventListener('dragover', function(e) {
        e.preventDefault();
        fileDisplay.style.borderColor = 'var(--primary-color)';
        fileDisplay.style.background = 'rgba(99, 102, 241, 0.05)';
    });

    fileDisplay.addEventListener('dragleave', function(e) {
        e.preventDefault();
        if (!fileInput.files[0]) {
            resetFileUpload();
        }
    });

    fileDisplay.addEventListener('drop', function(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

function resetFileUpload() {
    const fileText = document.querySelector('.file-text');
    const fileSubtext = document.querySelector('.file-subtext');
    const fileDisplay = document.querySelector('.file-upload-display');
    
    fileText.textContent = 'Drag & drop an image or click to browse';
    fileSubtext.textContent = 'Supports JPG, PNG, GIF up to 10MB';
    fileDisplay.style.borderColor = 'var(--border-color)';
    fileDisplay.style.background = 'rgba(99, 102, 241, 0.02)';
}

// Schedule toggle functionality
function initializeScheduleToggle() {
    const postNow = document.getElementById('post-now');
    const postLater = document.getElementById('post-later');
    const scheduleInput = document.getElementById('scheduleInput');

    if (!postNow || !postLater || !scheduleInput) return;

    postNow.addEventListener('change', function() {
        if (this.checked) {
            scheduleInput.style.display = 'none';
        }
    });

    postLater.addEventListener('change', function() {
        if (this.checked) {
            scheduleInput.style.display = 'block';
            // Set minimum datetime to 20 minutes from now
            const now = new Date();
            now.setMinutes(now.getMinutes() + 20);
            document.getElementById('schedule_time').min = now.toISOString().slice(0, 16);
        }
    });
}

// Loading state management
function showLoadingState() {
    const formContainer = document.querySelector('.form-container');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (formContainer) formContainer.style.display = 'none';
    if (loadingContainer) loadingContainer.style.display = 'block';
    if (resultsContainer) resultsContainer.style.display = 'none';
}

function hideLoadingState() {
    const formContainer = document.querySelector('.form-container');
    const loadingContainer = document.getElementById('loadingContainer');
    
    if (formContainer) formContainer.style.display = 'block';
    if (loadingContainer) loadingContainer.style.display = 'none';
}

// Progress simulation
function simulateProgress() {
    const steps = document.querySelectorAll('.step');
    let currentStep = 0;

    const progressInterval = setInterval(() => {
        if (currentStep < steps.length) {
            steps[currentStep].classList.add('active');
            currentStep++;
        } else {
            clearInterval(progressInterval);
        }
    }, 1500);

    // Store interval ID to clear it if needed
    window.progressInterval = progressInterval;
}

// Results parsing and display
function displayResults(caption, content, imageUrl) {
    const resultsContainer = document.getElementById('resultsContainer');
    const formContainer = document.querySelector('.form-container');
    
    // Update result content
    document.getElementById('generatedCaption').textContent = caption || 'No caption generated';
    document.getElementById('generatedContent').textContent = content || 'No content generated';
    
    // Handle image display
    const imageResult = document.getElementById('imageResult');
    const generatedImage = document.getElementById('generatedImage');
    
    if (imageUrl && imageUrl !== 'None') {
        generatedImage.src = imageUrl;
        imageResult.style.display = 'block';
    } else {
        imageResult.style.display = 'none';
    }
    
    // Show results
    if (formContainer) formContainer.style.display = 'none';
    if (resultsContainer) resultsContainer.style.display = 'block';
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Copy functionality
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const copyType = this.getAttribute('data-copy');
            let textToCopy = '';
            
            if (copyType === 'caption') {
                textToCopy = document.getElementById('generatedCaption').textContent;
            } else if (copyType === 'content') {
                textToCopy = document.getElementById('generatedContent').textContent;
            }
            
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    showSuccess('Copied to clipboard!');
                }).catch(() => {
                    showError('Failed to copy to clipboard');
                });
            }
        });
    });
}

// Flash message handling
function initializeFlashMessages() {
    const closeButtons = document.querySelectorAll('.close-flash');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.closest('.flash-message');
            if (flashMessage) {
                flashMessage.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => {
                    flashMessage.remove();
                }, 300);
            }
        });
    });

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            if (message.parentNode) {
                message.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => {
                    if (message.parentNode) {
                        message.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

// Utility functions for notifications
function showError(message) {
    showNotification(message, 'error');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showNotification(message, type = 'info') {
    const flashContainer = document.querySelector('.flash-messages') || createFlashContainer();
    
    const flashMessage = document.createElement('div');
    flashMessage.className = 'flash-message';
    flashMessage.innerHTML = `
        <i data-feather="${type === 'error' ? 'alert-circle' : type === 'success' ? 'check-circle' : 'info'}"></i>
        <span>${message}</span>
        <button class="close-flash">
            <i data-feather="x"></i>
        </button>
    `;
    
    flashContainer.appendChild(flashMessage);
    
    // Initialize feather icons for the new elements
    feather.replace();
    
    // Add close functionality
    const closeBtn = flashMessage.querySelector('.close-flash');
    closeBtn.addEventListener('click', function() {
        flashMessage.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => {
            flashMessage.remove();
        }, 300);
    });
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (flashMessage.parentNode) {
            flashMessage.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => {
                if (flashMessage.parentNode) {
                    flashMessage.remove();
                }
            }, 300);
        }
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Reset form function
function resetForm() {
    const form = document.getElementById('contentForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const formContainer = document.querySelector('.form-container');
    
    if (form) {
        form.reset();
        resetFileUpload();
    }
    
    if (resultsContainer) resultsContainer.style.display = 'none';
    if (formContainer) formContainer.style.display = 'block';
    
    // Reset schedule input
    const scheduleInput = document.getElementById('scheduleInput');
    if (scheduleInput) {
        scheduleInput.style.display = 'none';
    }
}

// Add reset button functionality if needed
document.addEventListener('click', function(e) {
    if (e.target.matches('.reset-btn')) {
        resetForm();
    }
});