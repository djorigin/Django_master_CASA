/**
 * Aircraft Type Management JavaScript
 * Handles CRUD operations for aircraft types
 */

// CSRF Token utility
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Message display utility
function showMessage(message, type) {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        ${message}
        <button type="button" class="close" onclick="this.parentElement.style.display='none'">
            <i class="fas fa-times"></i>
        </button>
    `;
    messagesContainer.appendChild(alertDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.querySelector('.page-content').insertBefore(container, document.querySelector('.page-content').firstChild);
    return container;
}

// Delete Aircraft Type
function deleteAircraftType(id, name) {
    if (confirm(`Are you sure you want to delete aircraft type "${name}"?`)) {
        fetch(`/aircraft/types/${id}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                location.reload();
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error deleting aircraft type', 'error');
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Aircraft Type Management JavaScript loaded');
    
    // Auto-hide messages after page load
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            if (message.style.display !== 'none') {
                message.style.opacity = '0.8';
            }
        }, 3000);
    });
});