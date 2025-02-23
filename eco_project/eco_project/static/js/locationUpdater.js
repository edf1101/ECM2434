import {getCookie} from "./cookieFetcher.js";

let lastSentTime = 0; // Timestamp of last update
let lastKnownPosition = null; // Stores last known location
let locationTrackingStarted = false;

/**
 * Send the user's location to the API
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 */
function sendLocation(lat, lon) {
    const currentTime = Date.now();

    if (currentTime - lastSentTime >= 5000) {  // Ensure updates every 5 seconds
        const absoluteLocURL = window.location.origin + updateLocURL;

        fetch(absoluteLocURL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
            body: new URLSearchParams({lat: lat, lon: lon})
        })
            .then(response => response.json())
            .then(data => {
                console.log('Location updated:', data);
                lastSentTime = currentTime;
            })
            .catch(error => {
                console.error('Error updating location:', error);
            });
    }
}

/**
 * Start watching user's location
 */
function startLocationTracking() {
    if (locationTrackingStarted) return; // Prevent multiple calls
    locationTrackingStarted = true;

    if (navigator.geolocation) {
        console.log("Starting geolocation tracking");

        // Use watchPosition for real-time tracking that doesn't require polling
        navigator.geolocation.watchPosition(
            position => {
                lastKnownPosition = position;
                sendLocation(position.coords.latitude, position.coords.longitude);
            },
            error => {
                console.error("Error obtaining location:", error);
            },
            {enableHighAccuracy: true, maximumAge: 5000, timeout: 15000} // Increased timeout
        );

        // Ensure updates every 5 seconds
        setInterval(() => {
            if (lastKnownPosition) {
                sendLocation(lastKnownPosition.coords.latitude, lastKnownPosition.coords.longitude);
            } else {
                console.warn("No location data yet.");
            }
        }, 5000);
    } else {
        console.error('Geolocation is not supported by this browser');
    }
}


// Attempt to start tracking immediately
document.addEventListener("DOMContentLoaded", function () {
    navigator.permissions.query({name: 'geolocation'}).then(permissionStatus => {
        if (permissionStatus.state === "granted") {
            startLocationTracking(); // Start instantly if allowed
        } else {
            console.log("Waiting for user interaction to start geolocation");
            document.addEventListener("scroll", startLocationTracking, {once: true});
            document.addEventListener("click", startLocationTracking, {once: true});
        }
    });
});