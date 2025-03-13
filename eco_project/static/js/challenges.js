// wait for the DOM to be loaded
document.addEventListener('DOMContentLoaded', function () {
    const alertsContainer = document.querySelector('.challenge-alerts-container');
    let challengeQueue = []; // we will store challenges we know about here

    /**
     * Fetch challenges from the API and store them in the queue
     */
    function fetchChallenges() {
        fetch(getNearbyChallengesURL)
            .then(response => response.json())
            .then(data => {
                // 1) Clear old alerts once, right after fetching
                alertsContainer.innerHTML = '';

                // 2) Reset the challenge queue
                challengeQueue = data.challenges || [];

                // 3) Now display up to 3 from the new queue
                displayAlerts();
            })
            .catch(error => {
                console.error('Error fetching challenges:', error);
            });
    }


    /**
     * Make sure 3 alerts are displayed at all times, unless out of challenges in queue
     */
    function displayAlerts() {
        let currentAlerts = alertsContainer.querySelectorAll('.alert').length;
        while (currentAlerts < 3 && challengeQueue.length > 0) {
            const challenge = challengeQueue.shift();
            const alertElem = createAlertElement(challenge);
            alertsContainer.appendChild(alertElem);
            currentAlerts++;
        }
    }


    /**
     * Create an alert element for a challenge
     *
     * @param challenge The challenge object to create an alert for
     * @return {HTMLDivElement} The alert element to display
     */
    function createAlertElement(challenge) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-custom-green alert-dismissible fade show';
        alertDiv.setAttribute('role', 'alert');

        // set the alert content
        alertDiv.innerHTML = `
      <strong>${challenge.directions}</strong>: ${challenge.description}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

        // On Bootstrap's closed event
        alertDiv.addEventListener('closed.bs.alert', function () {
            displayAlerts(); // try to add more from the queue

            // If no alerts are left and the queue is empty, fetch new data
            if (alertsContainer.querySelectorAll('.alert').length === 0 && challengeQueue.length === 0) {
                fetchChallenges();
            }
        });

        // in case it doesn't load properly
        alertDiv.querySelector('.btn-close').addEventListener('click', function () {
            setTimeout(displayAlerts, 300);
        });

        return alertDiv;
    }


    fetchChallenges(); // fetch challenges on page load
});
