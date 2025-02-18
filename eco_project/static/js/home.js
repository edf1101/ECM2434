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
     * This function just contains dummy data for now but will update the pet widget on the
     * home page with the current pet stats
     */
    function updatePetStats() {
        // dummy values
        const health = 50;
        const points = 100;

        // Set progress bar width and text
        const healthBar = document.getElementById('petHealthBar');
        healthBar.style.width = health + '%';
        healthBar.ariaValueNow = health;
        healthBar.textContent = health + '%';

        // Update health description
        const healthText = document.getElementById('petHealthText');
        if (health > 80) {
            healthText.textContent = 'Your pet is happy! Go find challenges to keep it that way!';
        } else if (health > 30) {
            healthText.textContent = 'Your pet is surviving, but not thriving. Find challenges to improve its health!';
        } else {
            healthText.textContent = 'Your pet is feeling sad, it doesnt want to go extinct! Find challenges to save it!';
        }

        // Update points display
        document.getElementById('petPoints').textContent = points;
    }

    updatePetStats(); // set initial values for pet stats
    updateUI(); // Initial UI state
    setInterval(updatePetStats, 5000); // update pet stats every 5s


});