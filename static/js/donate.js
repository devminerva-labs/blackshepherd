// Donation Form Enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Quick amount buttons functionality
    const quickAmountBtns = document.querySelectorAll('.quick-amount-btn');
    const amountRadios = document.querySelectorAll('input[name="amount"]');
    const customAmountInput = document.querySelector('input[name="custom_amount"]');
    const donateButton = document.querySelector('.donate-button');
    const donationForm = document.querySelector('#donation-form');
    
    // Quick amount button handlers
    quickAmountBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const amount = this.dataset.amount;
            
            // Remove active class from all buttons
            quickAmountBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Set the corresponding radio button
            const matchingRadio = document.querySelector(`input[value="${amount}"]`);
            if (matchingRadio) {
                matchingRadio.checked = true;
            }
            
            // Clear custom amount
            if (customAmountInput) {
                customAmountInput.value = '';
            }
            
            // Update donate button text
            updateDonateButtonText();
        });
    });
    
    // Amount radio button handlers
    amountRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove active class from quick buttons
            quickAmountBtns.forEach(btn => btn.classList.remove('active'));
            
            // If custom amount is selected, focus on input
            if (this.value === 'custom' && customAmountInput) {
                customAmountInput.focus();
            }
            
            updateDonateButtonText();
        });
    });
    
    // Custom amount input handler
    if (customAmountInput) {
        customAmountInput.addEventListener('input', function() {
            if (this.value) {
                // Select custom radio button
                const customRadio = document.querySelector('input[value="custom"]');
                if (customRadio) {
                    customRadio.checked = true;
                }
                
                // Remove active class from quick buttons
                quickAmountBtns.forEach(btn => btn.classList.remove('active'));
                
                updateDonateButtonText();
            }
        });
        
        customAmountInput.addEventListener('focus', function() {
            const customRadio = document.querySelector('input[value="custom"]');
            if (customRadio) {
                customRadio.checked = true;
            }
        });
        
        // Format input as user types
        customAmountInput.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.value = value.toFixed(2);
                }
            }
        });
    }
    
    // Update donate button text with amount
    function updateDonateButtonText() {
        if (!donateButton) return;
        
        const selectedRadio = document.querySelector('input[name="amount"]:checked');
        const currency = document.querySelector('select[name="currency"]').value;
        const buttonText = donateButton.querySelector('.button-text');
        
        if (selectedRadio && buttonText) {
            let amount = '';
            
            if (selectedRadio.value === 'custom') {
                const customValue = customAmountInput.value;
                if (customValue && !isNaN(parseFloat(customValue))) {
                    amount = formatCurrencyAmount(parseFloat(customValue), currency);
                }
            } else {
                amount = formatCurrencyAmount(parseFloat(selectedRadio.value), currency);
            }
            
            if (amount) {
                buttonText.textContent = `Donate ${amount}`;
            } else {
                buttonText.textContent = 'Donate Securely';
            }
        }
    }
    
    // Currency change handler
    const currencySelect = document.querySelector('select[name="currency"]');
    if (currencySelect) {
        currencySelect.addEventListener('change', updateDonateButtonText);
    }
    
    // Format currency amount
    function formatCurrencyAmount(amount, currency) {
        const symbols = {
            'NGN': '₦',
            'USD': '$',
            'GHS': 'GH₵',
            'ZAR': 'R',
            'KES': 'KSh'
        };
        
        const symbol = symbols[currency] || currency;
        return symbol + amount.toLocaleString();
    }
    
    // Form submission handling
    if (donationForm) {
        donationForm.addEventListener('submit', function(e) {
            const selectedAmount = document.querySelector('input[name="amount"]:checked');
            
            // Validation
            if (!selectedAmount) {
                e.preventDefault();
                showError('Please select a donation amount');
                return;
            }
            
            if (selectedAmount.value === 'custom') {
                const customValue = customAmountInput.value;
                if (!customValue || isNaN(parseFloat(customValue)) || parseFloat(customValue) <= 0) {
                    e.preventDefault();
                    showError('Please enter a valid custom amount');
                    customAmountInput.focus();
                    return;
                }
                
                const currency = currencySelect.value;
                const minAmount = currency === 'NGN' ? 100 : (currency === 'USD' ? 1 : 10);
                
                if (parseFloat(customValue) < minAmount) {
                    e.preventDefault();
                    const symbol = formatCurrencyAmount(minAmount, currency);
                    showError(`Minimum donation amount is ${symbol}`);
                    customAmountInput.focus();
                    return;
                }
            }
            
            // Show loading state
            if (donateButton) {
                const originalText = donateButton.querySelector('.button-text').textContent;
                donateButton.querySelector('.button-text').textContent = 'Processing...';
                donateButton.disabled = true;
                donateButton.classList.add('loading');
                
                // Backup: Re-enable after 15 seconds if something goes wrong
                setTimeout(() => {
                    if (donateButton.disabled) {
                        donateButton.querySelector('.button-text').textContent = originalText;
                        donateButton.disabled = false;
                        donateButton.classList.remove('loading');
                    }
                }, 15000);
            }
        });
    }
    
    // Error display function
    function showError(message) {
        // Remove existing error messages
        const existingErrors = document.querySelectorAll('.form-error-message');
        existingErrors.forEach(error => error.remove());
        
        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error-message flash-message flash-error';
        errorDiv.textContent = message;
        
        // Insert at top of form
        const formHeader = document.querySelector('.form-header');
        if (formHeader) {
            formHeader.parentNode.insertBefore(errorDiv, formHeader.nextSibling);
        }
        
        // Scroll to error
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
    
    // Share button functionality
    const shareButtons = document.querySelectorAll('.share-button');
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const campaignTitle = document.querySelector('.campaign-title').textContent;
            const campaignUrl = window.location.href;
            const campaignDescription = document.querySelector('.campaign-description').textContent;
            
            const shareData = {
                title: `Support: ${campaignTitle}`,
                url: campaignUrl,
                text: campaignDescription.substring(0, 100) + '...'
            };
            
            if (this.classList.contains('facebook')) {
                const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(campaignUrl)}`;
                window.open(facebookUrl, '_blank', 'width=600,height=400');
            } else if (this.classList.contains('twitter')) {
                const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareData.text)}&url=${encodeURIComponent(campaignUrl)}`;
                window.open(twitterUrl, '_blank', 'width=600,height=400');
            } else if (this.classList.contains('whatsapp')) {
                const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(shareData.text + ' ' + campaignUrl)}`;
                window.open(whatsappUrl, '_blank');
            } else if (this.classList.contains('email')) {
                const emailUrl = `mailto:?subject=${encodeURIComponent(shareData.title)}&body=${encodeURIComponent(shareData.text + '\n\n' + campaignUrl)}`;
                window.location.href = emailUrl;
            }
        });
    });
    
    // Initialize with first amount selected
    updateDonateButtonText();
    
    // Progress bar animation when page loads
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        const targetWidth = progressFill.style.width;
        progressFill.style.width = '0%';
        setTimeout(() => {
            progressFill.style.width = targetWidth;
        }, 500);
    }
    
    // Animate stat cards on scroll
    const statCards = document.querySelectorAll('.stat-card');
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.transform = 'translateY(0)';
                entry.target.style.opacity = '1';
            }
        });
    }, { threshold: 0.1 });
    
    statCards.forEach((card, index) => {
        card.style.transform = 'translateY(20px)';
        card.style.opacity = '0';
        card.style.transition = `all 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });
});

// Copy campaign link functionality
function copyCampaignLink() {
    const url = window.location.href;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Campaign link copied to clipboard!');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Campaign link copied to clipboard!');
    }
}

// Show notification function
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    
    // Add animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 300);
    }, 3000);
}