// Wait for the dom to load the content before running
document.addEventListener("DOMContentLoaded", function () {

    // get the create group button
    const createGroupBtn = document.getElementById('create-group-btn');

    if (createGroupBtn) { // and set it up
        createGroupBtn.addEventListener('click', function () {
            const nameInput = document.getElementById('group-name');
            const groupName = nameInput ? nameInput.value.trim() : "";
            const payload = groupName ? {name: groupName} : {};

            if (groupName === "" || groupName === null) { // check group is named
                alert("Group must be named");
                return;
            }

            // call the api to create the group
            fetch(window.createGroupUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify(payload)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.code) {
                        location.reload();
                    } else {
                        alert("Error creating group.");
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }

    // get the join group button
    const joinGroupBtn = document.getElementById('join-group-btn');

    if (joinGroupBtn) { // attach functionality to it
        joinGroupBtn.addEventListener('click', function () {
            const groupCode = document.getElementById('join-group-code').value.trim();
            if (!groupCode) { // make sure there is a group code in input box
                alert("Please enter a group code");
                return;
            }

            // call the API to handle the join group request
            fetch(window.joinGroupUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({"group_code": groupCode})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert(data.error || "Error joining group.");
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }

    // This code is for the delete group button, it can only be used by the admin of the group
    const deleteGroupBtns = document.querySelectorAll('.delete-group-btn');

    // there is a deleteGroupBtn for each accordian, go through them all and add functionality
    deleteGroupBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            // confirm the user is sure they want to delete the group
            if (confirm("Are you sure you want to delete this group?")) {
                // call the api
                fetch(btn.dataset.url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.csrfToken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload(); // reload the page to show new button
                        } else {
                            alert(data.error || "Error deleting group.");
                        }
                    })
                    .catch(error => console.error("Error:", error));
            }
        });
    });

    // This section is for removing users from a group. It can only be used by the group admin.
    const removeUserBtns = document.querySelectorAll('.remove-user-btn');

    // There is a remove user button for each user in each accordian, go through them all here
    removeUserBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const userId = btn.dataset.userId;

            if (confirm("Are you sure you want to remove this user from the group?")) {
                const url = btn.dataset.url;
                // call the API to remove the user
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.csrfToken
                    },
                    body: JSON.stringify({'user_id': userId})
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload(); // reload to update the removed user
                        } else {
                            alert(data.error || "Error removing user.");
                        }
                    })
                    .catch(error => console.error("Error:", error));
            }
        });
    });

    // This part is for leaving a group. Leave group can only be called by non admins
    const leaveGroupBtns = document.querySelectorAll('.leave-group-btn');
    // add functionality to the leave group button in each accordian
    leaveGroupBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {

            // confirm the user is sure they want to leave
            if (confirm("Are you sure you want to leave this group?")) {

                // call the API to leave a group
                fetch(btn.dataset.url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.csrfToken
                    }
                })
                    // after getting the JSON response if it is OK then reload the page
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert(data.error || "Error leaving group.");
                        }
                    })
                    // if there has been an error throw it here.
                    .catch(error => console.error("Error:", error));
            }
        });
    });
});
