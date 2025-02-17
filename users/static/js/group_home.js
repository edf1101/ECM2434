// Wait until the DOM is fully loaded then add event listeners to the create and join group buttons.

document.addEventListener("DOMContentLoaded", function () {

    // Create New Group Button
    const createGroupBtn = document.getElementById('create-group-btn');
    if (createGroupBtn) {
        createGroupBtn.addEventListener('click', function () {
            fetch(createGroupUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.code) { // redirect to the group's detail page upon successful creation
                        window.location.href = groupDetailUrlTemplate.replace('group_code_placeholder', data.code);
                    } else {
                        alert("Error creating group."); // display an error message if the group was not created
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }

    // Create the join group button event listener
    const joinGroupBtn = document.getElementById('join-group-btn');
    if (joinGroupBtn) {
        joinGroupBtn.addEventListener('click', function () {
            const groupCode = document.getElementById('join-group-code').value.trim();
            if (!groupCode) { // check if the group code is empty
                alert("Please enter a group code");
                return;
            }
            fetch(joinGroupUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({"group_code": groupCode})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Redirect to the group's page after joining.
                        window.location.href = groupDetailUrlTemplate.replace('group_code_placeholder', data.code);
                    } else {
                        alert(data.error || "Error joining group."); // display an error message if the user could not join the group
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }
});

