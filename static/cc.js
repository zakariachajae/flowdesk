document.addEventListener("DOMContentLoaded", async function () {
    await loadUsers();
    await loadTickets();
    await pouplateOptions();


    const searchInputTicket = document.querySelector('input[aria-label="Search ticket"]');
    const searchInputUser = document.querySelector('input[aria-label="Search user"]');
    const rowsPerPage = 8;
    const userTableBody = document.getElementById('userTableBody');
    const rows = Array.from(userTableBody.getElementsByTagName('tr'));
    const paginationContainer = document.getElementById('pagination');
    const entryInfo = document.getElementById('entryInfo');
    const startEntry = document.getElementById('startEntry');
    const endEntry = document.getElementById('endEntry');
    const totalEntries = document.getElementById('totalEntries');

    let currentPage = 1;

    function showPage(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });

        // Update entry info
        startEntry.textContent = start + 1;
        endEntry.textContent = Math.min(end, rows.length);
    }

    function setupPagination() {
        const pageCount = Math.ceil(rows.length / rowsPerPage);
        paginationContainer.innerHTML = '';

        for (let i = 1; i <= pageCount; i++) {
            const pageItem = document.createElement('li');
            pageItem.classList.add('page-item');
            if (i === currentPage) pageItem.classList.add('active');

            const pageLink = document.createElement('a');
            pageLink.classList.add('page-link');
            pageLink.href = '#';
            pageLink.textContent = i;

            pageLink.addEventListener('click', (event) => {
                event.preventDefault();
                document.querySelector('.pagination .page-item.active').classList.remove('active');
                pageItem.classList.add('active');
                currentPage = i;
                showPage(currentPage);
            });

            pageItem.appendChild(pageLink);
            paginationContainer.appendChild(pageItem);
        }

        // Enable/Disable prev and next buttons
        const prevButton = document.createElement('li');
        prevButton.classList.add('page-item', 'disabled');
        prevButton.innerHTML = `
            <a class="page-link" href="#" tabindex="-1" aria-disabled="true">
                <!-- Download SVG icon from http://tabler-icons.io/i/chevron-left -->
                <svg xmlns="http://www.w3.org/2000/svg" class="icon" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                    <path d="M15 6l-6 6l6 6" />
                </svg>
                prev
            </a>
        `;
        const nextButton = document.createElement('li');
        nextButton.classList.add('page-item');
        nextButton.innerHTML = `
            <a class="page-link" href="#">
                next <!-- Download SVG icon from http://tabler-icons.io/i/chevron-right -->
                <svg xmlns="http://www.w3.org/2000/svg" class="icon" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                    <path d="M9 6l6 6l-6 6" />
                </svg>
            </a>
        `;

        if (currentPage === 1) {
            prevButton.classList.add('disabled');
        } else {
            prevButton.classList.remove('disabled');
            prevButton.querySelector('a').addEventListener('click', (event) => {
                event.preventDefault();
                currentPage--;
                showPage(currentPage);
                document.querySelector('.pagination .page-item.active').classList.remove('active');
                paginationContainer.children[currentPage].classList.add('active');
            });
        }

        if (currentPage === pageCount) {
            nextButton.classList.add('disabled');
        } else {
            nextButton.classList.remove('disabled');
            nextButton.querySelector('a').addEventListener('click', (event) => {
                event.preventDefault();
                currentPage++;
                showPage(currentPage);
                document.querySelector('.pagination .page-item.active').classList.remove('active');
                paginationContainer.children[currentPage - 1].classList.add('active');
            });
        }

        paginationContainer.insertBefore(prevButton, paginationContainer.firstChild);
        paginationContainer.appendChild(nextButton);
    }

    setupPagination();
    showPage(1); // Show the first page by default

    // Update total entries
    totalEntries.textContent = rows.length;

  

    searchInputUser.addEventListener('input', (event) => {
        const searchTerm = event.target.value.toLowerCase();

        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            let found = false;

            for (let j = 1; j < cells.length - 1; j++) { // Skip the first cell (No.) and last cell (Actions)
                if (cells[j].innerText.toLowerCase().includes(searchTerm)) {
                    found = true;
                    break;
                }
            }

            rows[i].style.display = found ? '' : 'none';
        }
    });

    searchInputTicket.addEventListener('input', (event) => {
        const searchTerm = event.target.value.toLowerCase();

        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            let found = false;

            for (let j = 1; j < cells.length - 1; j++) { // Skip the first cell (No.) and last cell (Actions)
                if (cells[j].innerText.toLowerCase().includes(searchTerm)) {
                    found = true;
                    break;
                }
            }

            rows[i].style.display = found ? '' : 'none';
        }
    });


   

    async function loadUsers() {
        try {
            const response = await fetch("/users"); // Hardcoded user ID for example
            const users = await response.json();
            
        
            const userTableBody = document.getElementById("userTableBody");
            userTableBody.innerHTML = "";
            users.forEach(user => {
                const row = document.createElement("tr");
                row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.firstname}</td>
                <td>${user.lastname}</td>
                <td>${user.email}</td>
                <td>${user.created_at}</td>
                <td>${user.last_login_at}</td>
                <td>
                    <button class="btn btn-primary d-none d-sm-inline-block" data-bs-toggle="modal" data-bs-target="#editUserModal" data-user='${JSON.stringify(user)}'>Edit</button>
                </td>
            `;
                console.log(JSON.stringify(user))
                userTableBody.appendChild(row);
            });
            console.log("helloworld");
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
         

           


        } catch (error) {
            console.error("Error loading tickets:", error);
        }
    }

    async function pouplateOptions() {
        try {
            const response = await fetch("/users"); // Hardcoded user ID for example
            const users = await response.json();
            
            const assignedUserDropdown = document.getElementById("assignedUser");
            assignedUserDropdown.innerHTML = '<option value="">Unassigned</option>'; // Default unassigned option
            users.forEach(user => {
                const option = document.createElement("option");
                option.value = user.id;
                option.textContent = `${user.firstname} ${user.lastname}`;
                assignedUserDropdown.appendChild(option);
            });
    
            const editAssignedUserDropdown = document.getElementById("editAssignedUser");
            editAssignedUserDropdown.innerHTML = '<option value="">Unassigned</option>'; // Default unassigned option
            users.forEach(user => {
                const option = document.createElement("option");
                option.value = user.id;
                option.textContent = `${user.firstname} ${user.lastname}`;
                editAssignedUserDropdown.appendChild(option);
            });
           
    

         

           


        } catch (error) {
            console.error("Error loading tickets:", error);
        }
    }
    

    
    

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
    });

    async function loadTickets() {
        try {
            const response = await fetch("/tickets_admin?user_id=1"); // Hardcoded user ID for example
            const tickets = await response.json();

            const ticketTableBody = document.getElementById("ticketTableBody");
            ticketTableBody.innerHTML = ''; // Clear previous rows

            tickets.forEach(ticket => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${ticket.id}</td>
                    <td>${ticket.title}</td>
                    <td>${ticket.description}</td>
                    <td>${ticket.assigned_user_id ? ticket.assigned_user_fullname : "Unassigned"}</td>
                    <td>${ticket.status}</td>
                    <td><button class="btn btn-primary d-none d-sm-inline-block" data-bs-toggle="modal" data-bs-target="#editTicketModal" data-ticket='${JSON.stringify(ticket)}'>Edit</button></td>
                `;
                ticketTableBody.appendChild(row);
            });

            // Re-attach event listeners after dynamically loading the ticket rows
            const editTicketButtons = document.querySelectorAll('button[data-bs-target="#editTicketModal"]');
            editTicketButtons.forEach(button => {
                button.addEventListener('click', (event) => {
                    event.preventDefault();

                    // Parse the ticket data from the button's data attribute
                    const ticket = JSON.parse(button.getAttribute('data-ticket'));
                    console.log(ticket);

                    // Populate the form fields with the ticket data
                    document.getElementById('editTicketId').value = ticket.id;
                    document.getElementById('editTitle').value = ticket.title;
                    document.getElementById('editDescription').value = ticket.description;

                    // Check if the ticket has an assigned user, and set the value accordingly
                    const assignedUserSelect = document.getElementById('editAssignedUser');
                    if (ticket.assigned_user_id) {
                        assignedUserSelect.value = ticket.assigned_user_id;
                    } else {
                        assignedUserSelect.value = '';  // Leave it blank if no assigned user
                    }
                });
            });
            document.getElementById("editTicketForm").addEventListener("submit", async function (event) {
                event.preventDefault();
                const formData = new FormData(this);
                console.log(formData)
                const isActive = formData.get("is_active") === "on" ? true : false;
                formData.set("is_active", isActive);
                const response = await fetch("/update_ticket", {
                    method: "POST",
                    body: formData
                });
                if (!response.ok) {
                    console.error("Failed to update ticket:", response.status, response.statusText);
                    return;
                }
                const result = await response.json();
                alert(result.message || "Operation failed");
                location.reload();
                await loadTickets();

            });
            document.getElementById("addTicketForm").addEventListener("submit", async function (event) {
                event.preventDefault(); // Prevent form from submitting the default way
                const formData = new FormData(this);
            
                // Ensure that if the assigned user is unassigned, we set the value to null
                const assignedUser = formData.get("assigned_user_id");
                if (assignedUser === "" || assignedUser === "Unassigned") {
                    formData.set("assigned_user_id", null); // Set to null instead of deleting
                }
            
                try {
                    const response = await fetch("/create_ticket", {
                        method: "POST",
                        body: formData,
                    });
            
                    if (response.ok) {
                        alert("Ticket added successfully");
                        location.reload();
                        await loadTickets(); // Refresh tickets
                    } else {
                        alert("Error adding ticket");
                        console.error("Failed to add ticket:", response.statusText);
                    }
                } catch (error) {
                    console.error("Error adding ticket:", error);
                }
            });
        } catch (error) {
            console.error("Error loading tickets:", error);
        }
    }
    




  
  

   




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





// Load users into the user table and populate the "Assign to" dropdown for tickets



async function resetPassword() {
    const userId = document.getElementById("editUserId").value;
    const response = await fetch("/reset_password", {
        method: "POST",
        body: new URLSearchParams({ id: userId })
    });
    if (!response.ok) {
        console.error("Failed to reset password:", response.status, response.statusText);
        return;
    }
    const result = await response.json();
    alert(result.message || "Operation failed");
}
async function deleteUser() {
    const userId = document.getElementById("editUserId").value;
    if (confirm("Are you sure you want to delete this user?")) {
        const response = await fetch("/delete_user", {
            method: "POST",
            body: new URLSearchParams({ id: userId })
        });
        if (!response.ok) {
            console.error("Failed to delete user:", response.status, response.statusText);
            return;
        }
        const result = await response.json();
        alert(result.message || "Operation failed");
        location.reload();
        await loadUsers();

    }
}

async function deleteTicket() {
    const ticketId = document.getElementById("editTicketId").value;
    if (confirm("Are you sure you want to delete this ticket?")) {
        const response = await fetch("/delete_ticket", {
            method: "POST",
            body: new URLSearchParams({ id: ticketId })
        });
        if (!response.ok) {
            console.error("Failed to delete user:", response.status, response.statusText);
            return;
        }
        const result = await response.json();
        alert(result.message || "Operation failed");
        location.reload();
        await loadTickets();

    }
}












