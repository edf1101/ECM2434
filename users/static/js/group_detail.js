// Load this script on the group detail page after the DOM content is loaded
document.addEventListener("DOMContentLoaded", function () {

    // Delete Group Button (only available for admin)
    const deleteGroupBtn = document.getElementById('delete-group-btn');
    if (deleteGroupBtn) {
        deleteGroupBtn.addEventListener('click', function () {
            if (confirm("Are you sure you want to delete this group?")) { // check user is sure
                fetch(deleteGroupUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) { // if successful, redirect to group home page
                            window.location.href = groupHomeUrl;
                        } else { // if not successful throw error to user
                            alert(data.error || "Error deleting group.");
                        }
                    })
                    .catch(error => console.error("Error:", error));
            }
        });
    }

    // add the user removal buttons (admin only)
    const removeUserButtons = document.querySelectorAll('.remove-user-btn');
    removeUserButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            // check user is sure
            if (confirm("Are you sure you want to remove this user from the group?")) {
                fetch(removeUserUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({'user_id': userId})
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) { // reload page if successful to show updated user list
                            location.reload();
                        } else { // if error then throw to user
                            alert(data.error || "Error removing user.");
                        }
                    })
                    .catch(error => console.error("Error:", error));
            }
        });
    });

    // create action for leave group Button (only for non admin)
    const leaveGroupBtn = document.getElementById('leave-group-btn');
    if (leaveGroupBtn) {
        leaveGroupBtn.addEventListener('click', function () {
            // check user is sure
            if (confirm("Are you sure you want to leave this group?")) {
                fetch(leaveGroupUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) { // if successful, redirect to group home page
                            window.location.href = groupHomeUrl;
                        } else { // if not successful throw error to user
                            alert(data.error || "Error leaving group.");
                        }
                    })
                    .catch(error => console.error("Error:", error));
            }
        });
    }
});