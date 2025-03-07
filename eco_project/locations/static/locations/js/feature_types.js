// This script is used to load alerts on the feature type page

document.addEventListener('DOMContentLoaded', function () {
    // Retrieve nearby features from the saved data in the html file already
    const nearbyFeatures = JSON.parse(document.getElementById('nearby-features-data').textContent);
    const alertsContainer = document.getElementById('feature-alerts-container');

    let featureQueue = [...nearbyFeatures]; // Put initial data in the queue

    /**
     * Display alerts until there are 3 shown or the queue is empty.
     */
    function displayAlerts() {
        let currentAlerts = alertsContainer.querySelectorAll('.alert').length;
        while (currentAlerts < 3 && featureQueue.length > 0) {
            const feature = featureQueue.shift();
            const alertElem = createAlertElement(feature);
            alertsContainer.appendChild(alertElem);
            currentAlerts++;
        }
    }

    /**
     * Create an alert element for a feature instance.
     */
    function createAlertElement(feature) {
        const directions = feature.directions;
        const description = feature.description;

        // create alert itself
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-custom-green alert-dismissible fade show';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `<strong>${directions}</strong>: ${description}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;

        alertDiv.addEventListener('closed.bs.alert', function () {
            displayAlerts();
            // If no alerts left then fill queue again
            if (alertsContainer.querySelectorAll('.alert').length === 0 && featureQueue.length === 0) {
                featureQueue = [...nearbyFeatures];
                displayAlerts();
            }
        });

        // in case exit click doesnt work
        alertDiv.querySelector('.btn-close').addEventListener('click', function () {
            setTimeout(function () {
                displayAlerts();
                if (alertsContainer.querySelectorAll('.alert').length === 0 && featureQueue.length === 0) {
                    featureQueue = [...nearbyFeatures];
                    displayAlerts();
                }
            }, 300);
        });
        return alertDiv;
    }

    // set up initial alerts
    displayAlerts();
});
