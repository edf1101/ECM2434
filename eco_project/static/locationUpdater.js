import {getCookie} from "./cookieFetcher.js";

/**
 * Send the user's location to the API
 *
 * @param lat The user's latitude
 * @param lon The user's longitude
 */
function sendLocation(lat, lon) {
    fetch('users/api/update_location/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'), // needed to authenticate the user
        },
        credentials: 'include', // Ensures cookies (and therefore the session) are sent
        body: new URLSearchParams({
            lat: lat,
            lon: lon
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Location updated:', data);
        })
        .catch(error => {
            console.error('Error updating location:', error);
        });
}

// send initial location on load
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            sendLocation(lat, lon);
        },
        function (error) {
            console.error('Error obtaining location:', error);
        }
    );
}

// Send the user's location to the API every 20 seconds
setInterval(function () {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                sendLocation(lat, lon);
            },
            function (error) {
                console.error('Error obtaining location:', error);
            }
        );
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
}, 20 * 1000); // 20 seconds