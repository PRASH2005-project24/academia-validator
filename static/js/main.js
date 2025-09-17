// Academia Validator - Main JavaScript File
// Modern UI Functionality and Interactions

class AcademiaValidator {
    constructor() {
        this.selectedFile = null;
        this.isProcessing = false;
        this.offlineMode = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupOfflineDetection();
        this.setupServiceWorker();
        this.animateCounters();
        this.setupDropZone();
    }

    setupEventListeners() {
        // File input change
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelect(e.target.files[0]);
                }
            });
        }

        // Verify button click
        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', () => this.verifyCertificate());
        }

        // Navigation smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Form validation and submission
        this.setupFormValidation();
    }

    setupDropZone() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.highlight(uploadArea), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.unhighlight(uploadArea), false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e), false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(element) {
        element.classList.add('dragover');
    }

    unhighlight(element) {
        element.classList.remove('dragover');
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            this.handleFileSelect(files[0]);
        }
    }

    handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'image/bmp'];
        const maxSize = 16 * 1024 * 1024; // 16MB

        if (!allowedTypes.includes(file.type)) {
            this.showMessage('Invalid file type. Please upload PDF, PNG, JPG, JPEG, TIFF, or BMP files.', 'error');
            return;
        }

        if (file.size > maxSize) {
            this.showMessage('File size exceeds 16MB limit. Please choose a smaller file.', 'error');
            return;
        }

        this.selectedFile = file;
        this.updateUploadArea(file);
        
        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.disabled = false;
            verifyBtn.classList.remove('btn-secondary');
            verifyBtn.classList.add('btn-primary');
        }

        // Hide previous results
        this.hideResults();
        this.clearMessages();
    }

    updateUploadArea(file) {
        const uploadText = document.querySelector('.upload-text');
        const uploadHint = document.querySelector('.upload-hint');
        
        if (uploadText && uploadHint) {
            uploadText.textContent = `📄 Selected: ${file.name}`;
            uploadHint.textContent = `File size: ${this.formatFileSize(file.size)} • Click to select different file`;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async verifyCertificate() {
        if (!this.selectedFile) {
            this.showMessage('Please select a certificate file first.', 'error');
            return;
        }

        if (this.isProcessing) {
            return;
        }

        this.isProcessing = true;
        this.startProcessing();

        try {
            const formData = new FormData();
            formData.append('certificate', this.selectedFile);

            // Show progress
            this.updateProgress(10);

            const response = await fetch('/api/verify', {
                method: 'POST',
                body: formData
            });

            this.updateProgress(70);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.updateProgress(100);

            setTimeout(() => {
                this.hideProgress();
                this.stopProcessing();

                if (data.success) {
                    this.displayResults(data);
                    this.showMessage('Certificate verification completed successfully!', 'success');
                } else {
                    this.showMessage(`Verification failed: ${data.error}`, 'error');
                }
            }, 500);

        } catch (error) {
            console.error('Verification error:', error);
            this.hideProgress();
            this.stopProcessing();
            
            if (this.offlineMode) {
                this.showMessage('You are offline. Verification queued for when connection is restored.', 'warning');
            } else {
                this.showMessage('An error occurred during verification. Please try again.', 'error');
            }
        }
    }

    startProcessing() {
        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<span>⏳</span> Processing...';
            verifyBtn.classList.add('btn-loading');
        }
    }

    stopProcessing() {
        this.isProcessing = false;
        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<span>🔍</span> Verify Certificate';
            verifyBtn.classList.remove('btn-loading');
        }
    }

    updateProgress(percent) {
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        
        if (progressContainer && progressBar) {
            progressContainer.style.display = 'block';
            progressBar.style.width = percent + '%';
        }
    }

    hideProgress() {
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }

    displayResults(data) {
        // Update verification status
        const status = data.validation_result?.status || 'Processed';
        const statusElement = document.getElementById('verificationStatus');
        
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = 'result-status';
            
            // Add appropriate status class
            if (status.toLowerCase().includes('valid') && !status.toLowerCase().includes('invalid')) {
                statusElement.classList.add('valid');
            } else if (status.toLowerCase().includes('invalid')) {
                statusElement.classList.add('invalid');
            } else {
                statusElement.classList.add('suspicious');
            }
        }

        // Update confidence score
        const confidence = data.confidence_score || data.ocr_confidence || 0;
        const confidenceElement = document.getElementById('confidenceScore');
        if (confidenceElement) {
            confidenceElement.textContent = `${Math.round(confidence)}%`;
        }

        // Update extracted details
        const details = data.extracted_details || data.parsed_details || {};
        this.updateResultField('studentName', details.student_name);
        this.updateResultField('certNumber', details.certificate_number);
        this.updateResultField('institution', details.institution_name);
        this.updateResultField('gradYear', details.graduation_year);
        this.updateResultField('course', details.course_name);
        this.updateResultField('rollNumber', details.roll_number);
        this.updateResultField('cgpaGrade', details.cgpa_percentage);
        this.updateResultField('processingMethod', data.processing_method || 'Enhanced OCR');

        // Show results section
        this.showResults();

        // Animate result appearance
        this.animateResults();
    }

    updateResultField(fieldId, value) {
        const element = document.getElementById(fieldId);
        if (element) {
            element.textContent = value || 'Not found';
            
            // Add animation class
            element.classList.add('field-updated');
            setTimeout(() => {
                element.classList.remove('field-updated');
            }, 600);
        }
    }

    showResults() {
        const results = document.getElementById('results');
        if (results) {
            results.style.display = 'block';
            
            // Smooth scroll to results
            setTimeout(() => {
                results.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }

    hideResults() {
        const results = document.getElementById('results');
        if (results) {
            results.style.display = 'none';
        }
    }

    animateResults() {
        const resultCard = document.querySelector('.result-card');
        if (resultCard) {
            resultCard.classList.add('result-appear');
            
            // Animate each field with a slight delay
            const fields = document.querySelectorAll('.result-field');
            fields.forEach((field, index) => {
                setTimeout(() => {
                    field.classList.add('field-appear');
                }, index * 100);
            });
        }
    }

    showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('messageContainer');
        if (!messageContainer) return;

        const alertClass = `alert-${type}`;
        const icon = this.getMessageIcon(type);
        
        messageContainer.innerHTML = `
            <div class="alert ${alertClass}">
                <span>${icon}</span>
                ${message}
            </div>
        `;

        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                this.clearMessages();
            }, 5000);
        }
    }

    getMessageIcon(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };
        return icons[type] || icons['info'];
    }

    clearMessages() {
        const messageContainer = document.getElementById('messageContainer');
        if (messageContainer) {
            messageContainer.innerHTML = '';
        }
    }

    // Offline functionality
    setupOfflineDetection() {
        window.addEventListener('online', () => {
            this.offlineMode = false;
            this.updateOfflineStatus();
        });

        window.addEventListener('offline', () => {
            this.offlineMode = true;
            this.updateOfflineStatus();
        });

        // Initial status
        this.offlineMode = !navigator.onLine;
        this.updateOfflineStatus();
    }

    updateOfflineStatus() {
        const offlineIndicator = document.getElementById('offlineIndicator');
        if (offlineIndicator) {
            if (this.offlineMode) {
                offlineIndicator.classList.add('show');
            } else {
                offlineIndicator.classList.remove('show');
            }
        }
    }

    // Service Worker setup
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/sw.js')
                    .then((registration) => {
                        console.log('✅ Service Worker registered:', registration.scope);
                    })
                    .catch((error) => {
                        console.log('❌ Service Worker registration failed:', error);
                    });
            });
        }
    }

    // Counter animations
    animateCounters() {
        const counters = document.querySelectorAll('.hero-stat-number');
        
        const animateCounter = (counter) => {
            const target = counter.textContent;
            const numericValue = parseInt(target.replace(/[^\d]/g, ''));
            
            if (numericValue > 0) {
                let current = 0;
                const increment = numericValue / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= numericValue) {
                        current = numericValue;
                        clearInterval(timer);
                    }
                    counter.textContent = target.replace(/\d+/, Math.floor(current).toLocaleString());
                }, 40);
            }
        };

        // Use Intersection Observer for better performance
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        counters.forEach((counter) => {
            observer.observe(counter);
        });
    }

    // Form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });

        return isValid;
    }

    showFieldError(input, message) {
        input.classList.add('error');
        
        // Remove existing error message
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
    }

    clearFieldError(input) {
        input.classList.remove('error');
        const errorDiv = input.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Utility methods
    debounce(func, wait) {
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

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.academiaValidator = new AcademiaValidator();
    
    // Add some additional CSS animations
    const style = document.createElement('style');
    style.textContent = `
        .field-updated {
            animation: fieldUpdate 0.6s ease-in-out;
        }
        
        .result-appear {
            animation: resultAppear 0.8s ease-out;
        }
        
        .field-appear {
            animation: fieldAppear 0.5s ease-out forwards;
            opacity: 0;
            transform: translateY(20px);
        }
        
        @keyframes fieldUpdate {
            0% { background-color: var(--primary-green-lighter); }
            100% { background-color: transparent; }
        }
        
        @keyframes resultAppear {
            0% { opacity: 0; transform: scale(0.9) translateY(20px); }
            100% { opacity: 1; transform: scale(1) translateY(0); }
        }
        
        @keyframes fieldAppear {
            to { opacity: 1; transform: translateY(0); }
        }
        
        .btn-loading {
            pointer-events: none;
            opacity: 0.7;
        }
        
        .field-error {
            color: var(--error);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
        
        input.error, select.error, textarea.error {
            border-color: var(--error);
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
        }
    `;
    document.head.appendChild(style);
});

// Export for potential external use
window.AcademiaValidator = AcademiaValidator;