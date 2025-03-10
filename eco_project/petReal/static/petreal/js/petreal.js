// This script handles the requests for the petReal homepage, mainly for adding reactions to photos.

document.addEventListener("DOMContentLoaded", function() {
    const popup = document.getElementById('reaction-popup');
    // Initially hide the popup
    popup.style.display = 'none';

    // Handle click on the "add reaction" button
    const reactionContainers = document.querySelectorAll('.reaction-container');
    reactionContainers.forEach(container => {
        const addBtn = container.querySelector('.add-reaction');
        addBtn.addEventListener('click', (event) => {
            event.stopPropagation();  // Prevent event bubbling
            const photoUser = container.getAttribute('data-photo-user');

            // Toggle popup: if already open for this photo, hide it
            if (popup.style.display === 'block' && popup.getAttribute('data-photo-user') === photoUser) {
                popup.style.display = 'none';
                return;
            }

            // Set which photo the popup is for
            popup.setAttribute('data-photo-user', photoUser);

            // Calculate position relative to the clicked plus icon
            const rect = addBtn.getBoundingClientRect();
            popup.style.position = 'absolute';
            popup.style.left = rect.left + window.pageXOffset + "px";
            // Place popup just below the plus icon (with a 5px offset)
            popup.style.top = (rect.bottom + window.pageYOffset + 5) + "px";
            popup.style.display = 'block';
        });
    });

    // Hide popup when clicking/touching anywhere outside it
    document.addEventListener('click', function(event) {
        if (!popup.contains(event.target)) {
            popup.style.display = 'none';
        }
    });
    document.addEventListener('touchstart', function(event) {
        if (!popup.contains(event.target)) {
            popup.style.display = 'none';
        }
    });
    const carousel = document.querySelector('.photo-carousel');
    if (carousel) {
        carousel.addEventListener('scroll', () => {
            popup.style.display = 'none';
        });
    }

    // Handle selection of a reaction from the reaction selector popup
    const reactionOptions = document.querySelectorAll('.reaction-option');
    reactionOptions.forEach(option => {
        option.addEventListener('click', () => {
            const reaction = option.getAttribute('data-reaction');
            const photoUser = popup.getAttribute('data-photo-user');

            // Make a POST request to the API endpoint using the global variable
            fetch(window.addReactionUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    reaction: reaction,
                    photo_user: photoUser
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                // Refresh the page after the API call succeeds
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
            });

            // Hide the popup after selection
            popup.style.display = 'none';
        });
    });
});

/**
 * Get the value of a cookie by name.
 *
 * @param name {string} - The name of the cookie to
 * @returns {null} - The value of the cookie, or null if not found
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
