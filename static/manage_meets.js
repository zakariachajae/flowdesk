document.addEventListener("DOMContentLoaded", async function () {

    await pouplateOptions();
    await loadmeetings()


    document.addEventListener('DOMContentLoaded', () => {
        // Event listener for admin_dashboard link
        document.getElementById('admin_dashboard').addEventListener('click', async function (event) {
            event.preventDefault(); // Prevent default link behavior
            const response = await fetch('/get_admin_dashboard');
            if (response.ok) {
                const html = await response.text();
                document.getElementById('content').innerHTML = html; // Update the content area
            } else {
                console.error('Failed to fetch the admin dashboard');
            }
        });

        // Event listener for manage_tickets link
        document.getElementById('manage_tickets').addEventListener('click', async function (event) {
            event.preventDefault(); // Prevent default link behavior
            const response = await fetch('/manage_tickets');
            if (response.ok) {
                const html = await response.text();
                document.getElementById('content').innerHTML = html; // Update the content area
            } else {
                console.error('Failed to fetch manage tickets');
            }
        });
        document.getElementById('archives').addEventListener('click', async function (event) {
            event.preventDefault(); // Prevent default link behavior
            const response = await fetch('/archives');
            if (response.ok) {
                const html = await response.text();
                document.getElementById('content').innerHTML = html; // Update the content area
            } else {
                console.error('Failed to fetch manage tickets');
            }
        });

        document.getElementById('meetings').addEventListener('click', async function (event) {
            event.preventDefault(); // Prevent default link behavior
            const response = await fetch('/meeting');
            if (response.ok) {
                const html = await response.text();
                document.getElementById('content').innerHTML = html; // Update the content area
            } else {
                console.error('Failed to fetch manage tickets');
            }
        });


    });




});

document.getElementById("logout").addEventListener("click", async function (event) {
    event.preventDefault();
    const response = await fetch("/logout", { method: "POST" });
    if (response.redirected) {
        window.location.href = response.url;
    } else {
        console.error("Logout failed");
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('addMeetingForm');

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        // Get form values
        const subject = document.getElementById('meetingSubject').value;
        const startDate = document.getElementById('meetingDate').value;
        const participantIds = Array.from(document.getElementById('meetingParticipants').selectedOptions).map(option => option.value);


        // Prepare the payload
        const payload = {
            subject: subject,
            start_date: startDate,
            participantIds

        };

        try {
            // Send the request
            const response = await fetch('/create_meeting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            // Check if the response is OK
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            

            const data = await response.json();
            const meetingLink = data.eventLink;

            // Handle the response (e.g., show a success message, close the modal, etc.)
            alert('Meeting created successfully! Join link: ' + meetingLink);
            

            location.reload();
            return true

        } catch (error) {
            console.log("error is: ",error)
            alert('Failed to create meeting. Please try again.');
        }
    });
});

async function pouplateOptions() {
    try {
        const response = await fetch("/users"); // Hardcoded user ID for example
        const users = await response.json();

        const assignedUserDropdown = document.getElementById("meetingParticipants");
        // Default unassigned option
        users.forEach(user => {
            const option = document.createElement("option");
            option.value = user.email;
            option.textContent = `${user.firstname} ${user.lastname}`;
            assignedUserDropdown.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading tickets:", error);
    }
}

async function loadmeetings() {
    try {
        const response = await fetch("/meetings"); // Fetch meetings data
        const meetings = await response.json(); // Parse JSON response

        const meeting_cards = document.getElementById("meeting_cards");
        meeting_cards.innerHTML = ""; // Clear existing content

        meetings.forEach(meeting => {
            // Create card elements dynamically
            const card = document.createElement("div");
            card.className = "col-md-6 col-lg-3";

            card.innerHTML = `
                <div class="card">
                    <!-- Meeting Photo -->
                    <div class="img-responsive img-responsive-21x9 card-img-top"
                         style="background-image: url(/static/img/google.jpg)">
                    </div>
                    <div class="card-body">
                        <h3 class="card-title">${meeting.subject}</h3>
                        <p class="text-secondary">${meeting.date} </p>
                        <a href="${meeting.link}" target="_blank" class="btn btn-primary">Join</a> <!-- Join button -->
                    </div>
                </div>
            `;

            // Append the new card to the meeting_cards container
            meeting_cards.appendChild(card);
        });

    } catch (error) {
        console.error("Error loading meetings:", error);
    }
    /*console.log("helloworld");
    const editButtons = document.querySelectorAll('button[data-bs-target="#editUserModal"]');
    editButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const user = JSON.parse(button.getAttribute('data-user'));
            console.log(user);
            document.getElementById('editUserId').value = user.id;
            document.getElementById('editFirstname').value = user.firstname;
            document.getElementById('editLastname').value = user.lastname;
            document.getElementById('editEmail').value = user.email;
            document.getElementById('editIsActive').checked = user.is_active;
        });
    });

    document.getElementById("editUserForm").addEventListener("submit", async function (event) {
        event.preventDefault();
        const formData = new FormData(this);
        console.log(formData)
        const isActive = formData.get("is_active") === "on" ? true : false;
        formData.set("is_active", isActive);
        const response = await fetch("/update_user", {
            method: "POST",
            body: formData
        });
        if (!response.ok) {
            console.error("Failed to update user:", response.status, response.statusText);
            return;
        }
        const result = await response.json();
        alert(result.message || "Operation failed");
        location.reload();
        await loadUsers();

    });

    document.getElementById("addUserForm").addEventListener("submit", async function (event) {
        event.preventDefault();
        const formData = new FormData(this);
        const isActive = formData.get("is_active") === "on" ? true : false;
        formData.set("is_active", isActive);
        const response = await fetch("/create_user", {
            method: "POST",
            body: formData
        });
        if (!response.ok) {
            console.error("Failed to create user:", response.status, response.statusText);
            return;
        }
        const result = await response.json();
        alert(result.message);

        location.reload();
        await loadUsers();
    });



*/


}





