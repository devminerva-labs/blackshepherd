// Contact Form Enhancement
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    const submitBtn = contactForm.querySelector('.contact-submit-btn');
    const formInputs = contactForm.querySelectorAll('input, select, textarea');
    
    // Form validation patterns
    const validation = {
        email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        phone: /^[\+]?[1-9][\d]{0,15}$/,
        name: /^[a-zA-Z\s]{2,50}$/
    };
    
    // Real-time validation
    formInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
            // Real-time validation for certain fields
            if (this.name === 'email' && this.value) {
                setTimeout(() => validateField(this), 500);
            }
        });
        
        // Enhanced UX: Auto-format phone numbers
        if (input.name === 'phone') {
            input.addEventListener('input', formatPhoneNumber);
        }
    });
    
    // Form submission
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate all fields
        let isValid = true;
        formInputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        if (isValid) {
            submitForm();
        } else {
            scrollToFirstError();
            showFormError('Please fix the errors below before submitting.');
        }
    });
    
    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        const isRequired = field.required;
        
        // Clear previous errors
        clearFieldError(field);
        
        // Check if required field is empty
        if (isRequired && !value) {
            showFieldError(field, 'This field is required');
            return false;
        }
        
        // Skip validation if field is empty and not required
        if (!value && !isRequired) {
            return true;
        }
        
        // Specific field validations
        switch (fieldName) {
            case 'first_name':
            case 'last_name':
                if (!validation.name.test(value)) {
                    showFieldError(field, 'Please enter a valid name (2-50 characters, letters only)');
                    return false;
                }
                break;
                
            case 'email':
                if (!validation.email.test(value)) {
                    showFieldError(field, 'Please enter a valid email address');
                    return false;
                }
                // Check for common typos
                if (hasEmailTypo(value)) {
                    showFieldWarning(field, 'Please check your email address for typos');
                }
                break;
                
            case 'phone':
                const cleanPhone = value.replace(/\s|-|\(|\)/g, '');
                if (value && !validation.phone.test(cleanPhone)) {
                    showFieldError(field, 'Please enter a valid phone number');
                    return false;
                }
                break;
                
            case 'subject':
                if (!value) {
                    showFieldError(field, 'Please select a subject');
                    return false;
                }
                break;
                
            case 'message':
                if (value.length < 10) {
                    showFieldError(field, 'Please provide a more detailed message (at least 10 characters)');
                    return false;
                }
                if (value.length > 2000) {
                    showFieldError(field, 'Message is too long (maximum 2000 characters)');
                    return false;
                }
                break;
        }
        
        // If we get here, validation passed
        showFieldSuccess(field);
        return true;
    }
    
    function showFieldError(field, message) {
        const formGroup = field.closest('.form-group');
        const existingError = formGroup.querySelector('.field-error');
        
        if (existingError) {
            existingError.textContent = message;
        } else {
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            errorElement.textContent = message;
            errorElement.style.cssText = `
                color: #dc2626;
                font-size: 0.875rem;
                margin-top: 0.25rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            `;
            errorElement.innerHTML = `<span style="color: #dc2626;">⚠️</span> ${message}`;
            formGroup.appendChild(errorElement);
        }
        
        field.style.borderColor = '#dc2626';
        field.setAttribute('aria-invalid', 'true');
    }
    
    function showFieldWarning(field, message) {
        const formGroup = field.closest('.form-group');
        const existingWarning = formGroup.querySelector('.field-warning');
        
        if (!existingWarning) {
            const warningElement = document.createElement('div');
            warningElement.className = 'field-warning';
            warningElement.innerHTML = `<span style="color: #f59e0b;">⚠️</span> ${message}`;
            warningElement.style.cssText = `
                color: #f59e0b;
                font-size: 0.875rem;
                margin-top: 0.25rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            `;
            formGroup.appendChild(warningElement);
            
            // Auto-remove warning after 5 seconds
            setTimeout(() => {
                if (warningElement.parentNode) {
                    warningElement.parentNode.removeChild(warningElement);
                }
            }, 5000);
        }
    }
    
    function showFieldSuccess(field) {
        const formGroup = field.closest('.form-group');
        const existingSuccess = formGroup.querySelector('.field-success');
        
        if (!existingSuccess && field.value.trim()) {
            const successElement = document.createElement('div');
            successElement.className = 'field-success';
            successElement.innerHTML = `<span style="color: #16a34a;">✓</span>`;
            successElement.style.cssText = `
                color: #16a34a;
                font-size: 0.875rem;
                margin-top: 0.25rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            `;
            formGroup.appendChild(successElement);
            
            field.style.borderColor = '#16a34a';
            field.setAttribute('aria-invalid', 'false');
        }
    }
    
    function clearFieldError(field) {
        const formGroup = field.closest('.form-group');
        const errorElement = formGroup.querySelector('.field-error');
        const warningElement = formGroup.querySelector('.field-warning');
        const successElement = formGroup.querySelector('.field-success');
        
        if (errorElement) errorElement.remove();
        if (warningElement) warningElement.remove();
        if (successElement) successElement.remove();
        
        field.style.borderColor = '';
        field.removeAttribute('aria-invalid');
    }
    
    function scrollToFirstError() {
        const firstError = document.querySelector('.field-error');
        if (firstError) {
            const field = firstError.closest('.form-group').querySelector('input, select, textarea');
            field.scrollIntoView({ behavior: 'smooth', block: 'center' });
            field.focus();
        }
    }
    
    function hasEmailTypo(email) {
        const commonDomains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'];
        const emailParts = email.split('@');
        if (emailParts.length !== 2) return false;
        
        const domain = emailParts[1].toLowerCase();
        const commonTypos = {
            'gmial.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'yaho.com': 'yahoo.com',
            'outlok.com': 'outlook.com',
            'hotmial.com': 'hotmail.com'
        };
        
        return commonTypos[domain] !== undefined;
    }
    
    function formatPhoneNumber(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        if (value.startsWith('234')) {
            // Nigerian number format
            if (value.length <= 14) {
                value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{4})/, '+$1 $2 $3 $4');
            }
        } else if (value.startsWith('1')) {
            // US/Canada format
            if (value.length <= 11) {
                value = value.replace(/(\d{1})(\d{3})(\d{3})(\d{4})/, '+$1 ($2) $3-$4');
            }
        }
        
        e.target.value = value;
    }
    
    function submitForm() {
        // Show loading state
        const originalText = submitBtn.querySelector('.btn-text').textContent;
        const originalIcon = submitBtn.querySelector('.btn-icon').textContent;
        
        submitBtn.querySelector('.btn-text').textContent = 'Sending Message...';
        submitBtn.querySelector('.btn-icon').textContent = '⏳';
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        
        // Collect form data
        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData.entries());
        
        // Add timestamp and user agent for spam detection
        data.submitted_at = new Date().toISOString();
        data.user_agent = navigator.userAgent;
        data.referrer = document.referrer;
        
        // Simulate form submission (replace with actual endpoint)
        setTimeout(() => {
            // For demonstration - replace with actual fetch request
            simulateFormSubmission(data)
                .then(result => {
                    if (result.success) {
                        showSuccessMessage();
                        contactForm.reset();
                        
                        // Analytics tracking
                        if (typeof gtag !== 'undefined') {
                            gtag('event', 'form_submit', {
                                'form_name': 'contact_form',
                                'subject': data.subject
                            });
                        }
                    } else {
                        throw new Error(result.error || 'Submission failed');
                    }
                })
                .catch(error => {
                    showFormError('Failed to send message. Please try again or contact us directly.');
                    console.error('Form submission error:', error);
                })
                .finally(() => {
                    // Reset button state
                    submitBtn.querySelector('.btn-text').textContent = originalText;
                    submitBtn.querySelector('.btn-icon').textContent = originalIcon;
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('loading');
                });
        }, 1500); // Simulate network delay
    }
    
    // Simulated form submission - replace with real implementation
    function simulateFormSubmission(data) {
        return new Promise((resolve) => {
            // Simulate success/failure based on email domain for demo
            const isValid = data.email && !data.email.includes('test-fail');
            setTimeout(() => {
                resolve({
                    success: isValid,
                    error: isValid ? null : 'Invalid submission'
                });
            }, 1000);
        });
    }
    
    function showSuccessMessage() {
        const successDiv = document.createElement('div');
        successDiv.className = 'form-success-message';
        successDiv.innerHTML = `
            <div style="background: #dcfce7; border: 1px solid #bbf7d0; color: #166534; padding: 1.5rem; border-radius: 0.75rem; margin: 1rem 0; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #166534;">Message Sent Successfully!</h3>
                <p style="margin: 0; opacity: 0.8;">Thank you for reaching out. We'll get back to you within 24 hours.</p>
            </div>
        `;
        
        contactForm.insertBefore(successDiv, contactForm.firstChild);
        successDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 10000);
    }
    
    function showFormError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error-message';
        errorDiv.innerHTML = `
            <div style="background: #fee2e2; border: 1px solid #fecaca; color: #dc2626; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                <strong>❌ Error:</strong> ${message}
            </div>
        `;
        
        contactForm.insertBefore(errorDiv, contactForm.firstChild);
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 8000);
    }
    
    // Character counter for message field
    const messageField = document.querySelector('textarea[name="message"]');
    if (messageField) {
        const charCounter = document.createElement('div');
        charCounter.className = 'char-counter';
        charCounter.style.cssText = `
            text-align: right;
            font-size: 0.875rem;
            color: #6b7280;
            margin-top: 0.25rem;
        `;
        
        const updateCharCount = () => {
            const current = messageField.value.length;
            const max = 2000;
            charCounter.textContent = `${current}/${max} characters`;
            
            if (current > max * 0.9) {
                charCounter.style.color = '#dc2626';
            } else if (current > max * 0.75) {
                charCounter.style.color = '#f59e0b';
            } else {
                charCounter.style.color = '#6b7280';
            }
        };
        
        messageField.addEventListener('input', updateCharCount);
        messageField.parentNode.appendChild(charCounter);
        updateCharCount();
    }
    
    // Auto-save form data to prevent loss
    const autoSaveKey = 'contact_form_draft';
    
    function saveFormDraft() {
        const formData = {};
        formInputs.forEach(input => {
            if (input.name && input.value.trim()) {
                formData[input.name] = input.value.trim();
            }
        });
        
        if (Object.keys(formData).length > 0) {
            localStorage.setItem(autoSaveKey, JSON.stringify(formData));
        }
    }
    
    function loadFormDraft() {
        const saved = localStorage.getItem(autoSaveKey);
        if (saved) {
            try {
                const formData = JSON.parse(saved);
                Object.keys(formData).forEach(key => {
                    const field = document.querySelector(`[name="${key}"]`);
                    if (field) {
                        field.value = formData[key];
                    }
                });
                
                // Show notification about restored data
                showFormInfo('We restored your previous draft. You can continue where you left off.');
            } catch (error) {
                console.error('Error loading form draft:', error);
            }
        }
    }
    
    function clearFormDraft() {
        localStorage.removeItem(autoSaveKey);
    }
    
    function showFormInfo(message) {
        const infoDiv = document.createElement('div');
        infoDiv.innerHTML = `
            <div style="background: #dbeafe; border: 1px solid #93c5fd; color: #1e40af; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                <strong>ℹ️ Info:</strong> ${message}
            </div>
        `;
        
        contactForm.insertBefore(infoDiv, contactForm.firstChild);
        
        setTimeout(() => {
            if (infoDiv.parentNode) {
                infoDiv.parentNode.removeChild(infoDiv);
            }
        }, 5000);
    }
    
    // Auto-save every 30 seconds
    let autoSaveTimer;
    formInputs.forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(saveFormDraft, 30000);
        });
    });
    
    // Load draft on page load
    loadFormDraft();
    
    // Clear draft on successful submission
    contactForm.addEventListener('submit', () => {
        setTimeout(() => {
            if (document.querySelector('.form-success-message')) {
                clearFormDraft();
            }
        }, 2000);
    });
    
    // Prevent data loss on page unload
    window.addEventListener('beforeunload', (e) => {
        const hasUnsavedData = Array.from(formInputs).some(input => input.value.trim());
        if (hasUnsavedData) {
            saveFormDraft();
            e.preventDefault();
            e.returnValue = '';
        }
    });
});

// FAQ Accordion functionality
document.addEventListener('DOMContentLoaded', function() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        if (question) {
            question.style.cursor = 'pointer';
            question.addEventListener('click', function() {
                const answer = item.querySelector('.faq-answer');
                const isOpen = answer.style.display === 'block';
                
                // Close all other FAQ items
                faqItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        const otherAnswer = otherItem.querySelector('.faq-answer');
                        otherAnswer.style.display = 'none';
                        otherItem.classList.remove('active');
                    }
                });
                
                // Toggle current item
                if (isOpen) {
                    answer.style.display = 'none';
                    item.classList.remove('active');
                } else {
                    answer.style.display = 'block';
                    item.classList.add('active');
                }
            });
        }
    });
});

// Enhanced accessibility features
document.addEventListener('DOMContentLoaded', function() {
    // Add ARIA labels and descriptions
    const formFields = document.querySelectorAll('input, select, textarea');
    formFields.forEach(field => {
        if (!field.getAttribute('aria-label') && field.labels && field.labels.length > 0) {
            field.setAttribute('aria-label', field.labels[0].textContent.replace('*', '').trim());
        }
    });
    
    // Add keyboard navigation for custom elements
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close any open modals or notifications
            const notifications = document.querySelectorAll('.form-success-message, .form-error-message, .form-info-message');
            notifications.forEach(notification => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            });
        }
    });
    
    // Focus management
    const submitButton = document.querySelector('.contact-submit-btn');
    if (submitButton) {
        submitButton.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 0 3px rgba(255, 107, 53, 0.3)';
        });
        
        submitButton.addEventListener('blur', function() {
            this.style.boxShadow = '';
        });
    }
});

// Performance optimization: Debounce validation
function debounce(func, wait) {
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