// This script is used to load alerts on the feature type page

document.addEventListener('DOMContentLoaded', function () {
    // Retrieve nearby features from the saved data in the html file already
    const nearbyFeatures = JSON.parse(document.getElementById('nearby-features-data').textContent);
    const quizData = JSON.parse(document.getElementById('quizzes-data').textContent);
    const alertsContainerFeatures = document.getElementById('feature-alerts-container');
    const alertsContainerQuizzes = document.getElementById('challenge-alerts-container');

    let featureQueue = [...nearbyFeatures]; // Put initial data in the queue
    let challengeQueue = [...quizData]; // Put initial data in the queue

    /**
     * Display alerts until there are 3 shown or the queue is empty.
     */
    function displayAlerts() {
        let currentAlertsFeatures = alertsContainerFeatures.querySelectorAll('.alert').length;
        while (currentAlertsFeatures < 3 && featureQueue.length > 0) {
            const feature = featureQueue.shift();
            const alertElem = createFeatureAlert(feature);
            alertsContainerFeatures.appendChild(alertElem);
            currentAlertsFeatures++;
        }
        let currentAlertsChallenges = alertsContainerQuizzes.querySelectorAll('.alert').length;
        while (currentAlertsChallenges < 3 && challengeQueue.length > 0) {
            const challenge = challengeQueue.shift();
            const alertElem = createChallengeAlert(challenge);
            alertsContainerQuizzes.appendChild(alertElem);
            currentAlertsChallenges++;
        }

    }

    /**
     * Create an alert element for a feature instance.
     */
    function createFeatureAlert(feature) {
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
            if (alertsContainerFeatures.querySelectorAll('.alert').length === 0 && featureQueue.length === 0) {
                featureQueue = [...nearbyFeatures];
                displayAlerts();
            }
        });

        // in case exit click doesnt work
        alertDiv.querySelector('.btn-close').addEventListener('click', function () {
            setTimeout(function () {
                displayAlerts();
                if (alertsContainerFeatures.querySelectorAll('.alert').length === 0 && featureQueue.length === 0) {
                    featureQueue = [...nearbyFeatures];
                    displayAlerts();
                }
            }, 300);
        });
        return alertDiv;
    }

    /**
     * Create an alert element for a feature instance.
     */
    function createChallengeAlert(challenge) {
        const points = challenge.points;
        const url = challenge.url;
        const title = challenge.title;

        // create alert itself
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-custom-green alert-dismissible fade show';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `<strong>${title}</strong>: for ${points} points
                      <a href="${url}" class="profileLink">Take Quiz</a>
                      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;


        alertDiv.addEventListener('closed.bs.alert', function () {
            displayAlerts();
            // If no alerts left then fill queue again
            if (alertsContainerQuizzes.querySelectorAll('.alert').length === 0 && challengeQueue.length === 0) {
                challengeQueue = [...quizData];
                displayAlerts();
            }
        });

        // in case exit click doesnt work
        alertDiv.querySelector('.btn-close').addEventListener('click', function () {
            setTimeout(function () {
                displayAlerts();
                if (alertsContainerQuizzes.querySelectorAll('.alert').length === 0 && challengeQueue.length === 0) {
                    challengeQueue = [...quizData];
                    displayAlerts();
                }
            }, 300);
        });
        return alertDiv;
    }

    // set up initial alerts
    displayAlerts();
});
