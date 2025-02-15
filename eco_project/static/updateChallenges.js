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
    console.log(data);
})
.catch(error => {
    console.error("Error calling the API:", error);
});
