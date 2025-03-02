import {getCookie} from "./cookieFetcher.js";

const absoluteStreakURL = window.location.origin + streakURL;
fetch(absoluteStreakURL, {
    method: "POST",
    credentials: "include", // Include cookies for post req
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken // CSRF token for Django
    }
})
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error("Error calling the API:", error);
    });
