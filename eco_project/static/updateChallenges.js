import {getCookie} from "./cookieFetcher.js";


fetch("challenges/update_streak/", {
    method: "POST",
    credentials: "include", // Include cookies for session auth
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken") // CSRF token for Django
    }
})
    .then(response => response.json())
    .then(data => {
        // Log data to the console for debugging
        console.log(data);
        // Display the API response in the #streak-message div
        // const msgDiv = document.getElementById("streak-message");
        alert('${data.message}Your current streak is: ${data.streak}');
    })
    .catch(error => {
        console.error("Error calling the API:", error);
    });
