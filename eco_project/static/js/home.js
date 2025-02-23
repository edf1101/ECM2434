// wait for dom to load before running
document.addEventListener('DOMContentLoaded', () => {

    // Carousel arrow logic to select between map and pet (only for mobile)
    const featuresCarousel = document.getElementById('featuresCarousel');
    const arrowLeft = document.getElementById('arrowLeft');
    const arrowRight = document.getElementById('arrowRight');
    const label = document.getElementById('activeFeatureLabel');

    /**
     * Update the UI based on the current scroll position of the carousel
     * This is just highlighting the current feature and disabling the arrows when at the edges
     */
    function updateUI() {
        // get max and current horizontal scroll
        const maxScroll = featuresCarousel.scrollWidth - featuresCarousel.clientWidth;
        const currentScroll = featuresCarousel.scrollLeft;

        // Update label and arrows depending on which side of the carousel we are on
        label.textContent = currentScroll < maxScroll / 2 ? "Map" : "Pet";
        arrowLeft.disabled = currentScroll <= 0;
        arrowRight.disabled = currentScroll >= maxScroll;
    }

    // Add event listeners to the arrows
    arrowLeft.addEventListener('click', function () {
        arrowLeft.blur();
        arrowRight.blur();

        featuresCarousel.scrollTo({
            left: 0,
            behavior: 'smooth'
        });
    });
    arrowRight.addEventListener('click', function () {
        // Clear any focus/pressed state
        arrowLeft.blur();
        arrowRight.blur();

        const maxScroll = featuresCarousel.scrollWidth - featuresCarousel.clientWidth;
        featuresCarousel.scrollTo({
            left: maxScroll,
            behavior: 'smooth'
        });
    });

    featuresCarousel.addEventListener('scroll', updateUI); // update ui on scroll
    window.addEventListener('resize', () => { // update ui on resize
        arrowLeft.blur();
        arrowRight.blur();
        updateUI();
    });

    /**
     * This function updates the home page with the current pet stats
     */
    function updatePetStats() {
        // If the user is not signed in, keep the default values.
        if (!currentUsername) {
            console.log("User not signed in, using default pet data.");
            return;
        }

        // Helper function to retrieve the CSRF token (required for POST requests in Django)
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

        const csrftoken = getCookie('csrftoken');

        // Use the apiBaseUrl variable provided from the template and append the username.
        const apiUrl = baseApiUrlPet;

        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
            .then(response => {
                if (response.status === 404) {
                    console.log("No pet found for this user, using default values.");
                    // Return null so the following then block can skip UI updates.
                    return null;
                } else if (!response.ok) {
                    throw new Error("Error fetching pet data");
                }
                return response.json();
            })
            .then(data => {
                // If data is null, exit the function.
                if (!data) {
                    console.log("No pet data found, using default values.");
                    return;
                }

                // Update pet points
                document.getElementById('petPoints').textContent = data.user_points;

                // Update pet name
                document.getElementById('petName').textContent = data.pet_name;

                // Update health bar and text
                const health = data.pet_health;
                const healthBar = document.getElementById('petHealthBar');
                healthBar.style.width = health + '%';
                healthBar.setAttribute('aria-valuenow', health);
                healthBar.textContent = health + '%';

                const healthText = document.getElementById('petHealthText');
                if (health > 80) {
                    healthText.textContent = 'Your pet is happy! Go find challenges to keep it that way!';
                } else if (health > 30) {
                    healthText.textContent = 'Your pet is surviving, but not thriving. Find challenges to improve its health!';
                } else {
                    healthText.textContent = 'Your pet is feeling sad, it doesn\'t want to go extinct! Find challenges to save it!';
                }

                // Update pet image
                document.getElementById('petImage').src = data.pet_image;
            })
            .catch(error => {
                console.error('Error fetching pet data:', error);
            });
    }

// Run the update function when the DOM is fully loaded.
    document.addEventListener("DOMContentLoaded", updatePetStats);


// Run the update function when the DOM is fully loaded.
    document.addEventListener("DOMContentLoaded", updatePetStats);


    updatePetStats(); // set initial values for pet stats
    updateUI(); // Initial UI state
    setInterval(updatePetStats, 5000); // update pet stats every 5s


});