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

    updateUI(); // Initial UI state
});