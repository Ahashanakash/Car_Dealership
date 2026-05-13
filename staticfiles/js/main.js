// Handle review update events
document.body.addEventListener('reviewUpdated', function(evt) {
    const reviewId = evt.detail.reviewId;
    const reviewElement = document.getElementById(`review-${reviewId}`);
    
    if (reviewElement) {
        // Add highlight class
        reviewElement.classList.add('updated');
        
        // Remove highlight after 2 seconds
        setTimeout(() => {
            reviewElement.classList.remove('updated');
        }, 2000);
        
        // Scroll to the updated review
        reviewElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});

// Handle review deletion
document.body.addEventListener('reviewDeleted', function(evt) {
    const carId = evt.detail.carId;
    
    // Refresh the review form to allow new review
    htmx.ajax('GET', `/review/car/${carId}/review-form/`, '#review-form-container');
    
    // Show notification (optional)
    showNotification('Review deleted successfully');
});

// Handle form submission success
document.body.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.successful && evt.detail.target.classList.contains('review-form')) {
        // Clear form if it was a successful submission
        const form = evt.detail.target.querySelector('form');
        if (form) {
            form.reset();
        }
    }
});

// Handle form validation errors
document.body.addEventListener('htmx:responseError', function(evt) {
    if (evt.detail.xhr.status === 400) {
        showNotification('Please check your review and try again', 'error');
    }
});

// Notification function (optional)
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 20px;
        background-color: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        border-radius: 4px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);


function toggleBrands(){
    document.getElementById("brandMenu").classList.toggle("d-none");
}