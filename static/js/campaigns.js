// Campaigns Page Functionality
document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.querySelector('#sort-campaigns');
    const filterSelect = document.querySelector('#filter-category');
    const campaignsContainer = document.querySelector('#campaigns-container');
    const loadMoreBtn = document.querySelector('#load-more-btn');
    
    let allCampaigns = [];
    let visibleCampaigns = 6; // Show 6 campaigns initially
    
    // Initialize campaigns data
    function initializeCampaigns() {
        const campaignCards = document.querySelectorAll('.campaign-card');
        allCampaigns = Array.from(campaignCards).map(card => {
            return {
                element: card,
                title: card.querySelector('.campaign-title a').textContent,
                category: card.dataset.category,
                progress: parseFloat(card.dataset.progress),
                goal: parseFloat(card.dataset.goal),
                createdAt: new Date() // In real app, this would come from database
            };
        });
        
        updateVisibleCampaigns();
    }
    
    // Sort campaigns
    function sortCampaigns(criteria) {
        let sortedCampaigns = [...allCampaigns];
        
        switch(criteria) {
            case 'newest':
                sortedCampaigns.sort((a, b) => b.createdAt - a.createdAt);
                break;
            case 'progress':
                sortedCampaigns.sort((a, b) => b.progress - a.progress);
                break;
            case 'amount':
                sortedCampaigns.sort((a, b) => b.goal - a.goal);
                break;
            case 'popular':
                // Sort by number of supporters (transactions)
                sortedCampaigns.sort((a, b) => {
                    const aSupporters = parseInt(a.element.querySelector('.progress-supporters').textContent);
                    const bSupporters = parseInt(b.element.querySelector('.progress-supporters').textContent);
                    return bSupporters - aSupporters;
                });
                break;
        }
        
        return sortedCampaigns;
    }
    
    // Filter campaigns by category
    function filterCampaigns(campaigns, category) {
        if (category === 'all') {
            return campaigns;
        }
        return campaigns.filter(campaign => campaign.category === category);
    }
    
    // Update visible campaigns in DOM
    function updateVisibleCampaigns() {
        const sortCriteria = sortSelect ? sortSelect.value : 'newest';
        const filterCategory = filterSelect ? filterSelect.value : 'all';
        
        let filteredCampaigns = filterCampaigns(allCampaigns, filterCategory);
        let sortedCampaigns = sortCampaigns(filteredCampaigns);
        
        // Hide all campaigns first
        allCampaigns.forEach(campaign => {
            campaign.element.style.display = 'none';
        });
        
        // Show visible campaigns
        sortedCampaigns.slice(0, visibleCampaigns).forEach((campaign, index) => {
            campaign.element.style.display = 'block';
            campaign.element.style.animationDelay = `${index * 0.1}s`;
        });
        
        // Update load more button
        if (loadMoreBtn) {
            if (sortedCampaigns.length > visibleCampaigns) {
                loadMoreBtn.style.display = 'block';
                loadMoreBtn.textContent = `Load More (${sortedCampaigns.length - visibleCampaigns} remaining)`;
            } else {
                loadMoreBtn.style.display = 'none';
            }
        }
        
        // Update results count
        updateResultsCount(sortedCampaigns.length, filteredCampaigns.length);
    }
    
    // Update results count display
    function updateResultsCount(showing, total) {
        let countElement = document.querySelector('.results-count');
        if (!countElement) {
            countElement = document.createElement('div');
            countElement.className = 'results-count';
            countElement.style.cssText = `
                text-align: center;
                color: var(--gray-600);
                margin-bottom: var(--space-6);
                font-size: var(--font-size-sm);
            `;
            
            const filtersElement = document.querySelector('.campaigns-filters');
            if (filtersElement) {
                filtersElement.parentNode.insertBefore(countElement, filtersElement.nextSibling);
            }
        }
        
        if (showing === total) {
            countElement.textContent = `Showing all ${total} campaigns`;
        } else {
            countElement.textContent = `Showing ${Math.min(showing, visibleCampaigns)} of ${showing} campaigns`;
        }
    }
    
    // Event listeners
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            visibleCampaigns = 6; // Reset visible count when sorting
            updateVisibleCampaigns();
        });
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            visibleCampaigns = 6; // Reset visible count when filtering
            updateVisibleCampaigns();
        });
    }
    
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            visibleCampaigns += 6; // Load 6 more campaigns
            updateVisibleCampaigns();
            
            // Scroll to the first newly loaded campaign
            const allVisible = document.querySelectorAll('.campaign-card[style*="display: block"]');
            if (allVisible.length >= visibleCampaigns - 5) {
                allVisible[visibleCampaigns - 6].scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        });
    }
    
    // Initialize
    if (campaignsContainer) {
        initializeCampaigns();
    }
});

// Share campaign functionality
function shareCampaign(title, url) {
    if (navigator.share) {
        navigator.share({
            title: `Support: ${title}`,
            text: `Help support this important cause: ${title}`,
            url: url
        }).catch(err => {
            console.log('Error sharing:', err);
            fallbackShare(title, url);
        });
    } else {
        fallbackShare(title, url);
    }
}

function fallbackShare(title, url) {
    // Create share modal
    const modal = document.createElement('div');
    modal.className = 'share-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        max-width: 400px;
        width: 90%;
        text-align: center;
    `;
    
    modalContent.innerHTML = `
        <h3 style="margin-bottom: 1rem;">Share Campaign</h3>
        <p style="margin-bottom: 1.5rem; color: #666;">${title}</p>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1.5rem;">
            <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}" 
               target="_blank" 
               style="padding: 0.75rem; background: #1877f2; color: white; text-decoration: none; border-radius: 0.5rem;">
                Facebook
            </a>
            <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}" 
               target="_blank"
               style="padding: 0.75rem; background: #1da1f2; color: white; text-decoration: none; border-radius: 0.5rem;">
                Twitter
            </a>
            <a href="https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}" 
               target="_blank"
               style="padding: 0.75rem; background: #25d366; color: white; text-decoration: none; border-radius: 0.5rem;">
                WhatsApp
            </a>
            <button onclick="copyToClipboard('${url}')" 
                    style="padding: 0.75rem; background: #666; color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
                Copy Link
            </button>
        </div>
        <button onclick="closeModal()" 
                style="padding: 0.5rem 1rem; background: #ddd; border: none; border-radius: 0.5rem; cursor: pointer;">
            Close
        </button>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Global functions for modal
    window.closeModal = function() {
        if (modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
    };
    
    window.copyToClipboard = function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Link copied to clipboard!');
                closeModal();
            });
        } else {
            // Fallback
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showNotification('Link copied to clipboard!');
            closeModal();
        }
    };
}

// Toggle favorite functionality
function toggleFavorite(campaignId) {
    const favorites = JSON.parse(localStorage.getItem('favoriteCampaigns') || '[]');
    const index = favorites.indexOf(campaignId);
    
    if (index > -1) {
        favorites.splice(index, 1);
        showNotification('Removed from favorites');
    } else {
        favorites.push(campaignId);
        showNotification('Added to favorites');
    }
    
    localStorage.setItem('favoriteCampaigns', JSON.stringify(favorites));
    updateFavoriteButtons();
}

// Update favorite buttons display
function updateFavoriteButtons() {
    const favorites = JSON.parse(localStorage.getItem('favoriteCampaigns') || '[]');
    const favoriteButtons = document.querySelectorAll('.quick-action-btn');
    
    favoriteButtons.forEach(button => {
        if (button.onclick && button.onclick.toString().includes('toggleFavorite')) {
            const campaignId = extractCampaignId(button.onclick.toString());
            const icon = button.querySelector('.action-icon');
            
            if (favorites.includes(parseInt(campaignId))) {
                icon.textContent = '❤️';
                button.style.borderColor = 'var(--primary-color)';
                button.style.color = 'var(--primary-color)';
            } else {
                icon.textContent = '🤍';
                button.style.borderColor = 'var(--gray-300)';
                button.style.color = 'var(--gray-600)';
            }
        }
    });
}

// Helper function to extract campaign ID from onclick string
function extractCampaignId(onclickString) {
    const match = onclickString.match(/toggleFavorite\((\d+)\)/);
    return match ? match[1] : null;
}

// Show notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success-color);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: var(--shadow-lg);
        z-index: 10001;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, 3000);
}

// Animate campaigns on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const campaignObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Initialize animations when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Animate campaign cards
    const campaignCards = document.querySelectorAll('.campaign-card');
    campaignCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        card.style.transitionDelay = `${index * 0.1}s`;
        campaignObserver.observe(card);
    });
    
    // Initialize favorite buttons
    updateFavoriteButtons();
    
    // Smooth scroll for CTA button
    const ctaButton = document.querySelector('a[href="#campaigns-container"]');
    if (ctaButton) {
        ctaButton.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector('#campaigns-container');
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        });
    }
});