document.getElementById("logoutLink").addEventListener("click", async function (event) {
    event.preventDefault();
    console.log("Logout link clicked");  // Log statement
    const response = await fetch("/logout", {
        method: "POST"
    });
    if (response.redirected) {
        console.log("Redirecting to:", response.url);  // Log statement
        window.location.href = response.url;
    } else {
        console.error("Logout failed");
    }
});

document.addEventListener("DOMContentLoaded", async function () {
    await loadUsers();
});

async function loadUsers() {
    const response = await fetch("/users");
    if (!response.ok) {
        console.error("Failed to load users:", response.status, response.statusText);
        return;
    }
    const users = await response.json();
    renderUserTable(users);
}
function renderUserTable(users) {
    const userTableBody = document.getElementById("userTableBody");
    userTableBody.innerHTML = "";
    users.forEach(user => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${user.firstname}</td>
            <td>${user.lastname}</td>
            <td>${user.email}</td>
            <td>${user.created_at}</td>
            <td>${user.last_login_at}</td>
            <td>
                <button onclick="openEditUserModal(this)" data-user='${JSON.stringify(user)}'>Edit</button>
            </td>
        `;
        userTableBody.appendChild(row);
    });
}
function openAddUserModal() {
    document.getElementById("addUserModal").style.display = "block";
}
function closeAddUserModal() {
    document.getElementById("addUserModal").style.display = "none";
}
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
    closeAddUserModal();
    await loadUsers();
});
function openEditUserModal(button) {
    const user = JSON.parse(button.getAttribute('data-user'));
    document.getElementById("editUserId").value = user.id;
    document.getElementById("editFirstname").value = user.firstname;
    document.getElementById("editLastname").value = user.lastname;
    document.getElementById("editEmail").value = user.email;
    document.getElementById("editIsActive").checked = user.is_active;
    document.getElementById("editUserModal").style.display = "block";
}
function closeEditUserModal() {
    document.getElementById("editUserModal").style.display = "none";
}
document.getElementById("editUserForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(this);
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
    closeEditUserModal();
    await loadUsers();
});
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
        closeEditUserModal();
        await loadUsers();
    }
}
function sortAndFilterTable(columnIndex) {
    const table = document.getElementById("userTable");
    let direction = table.getAttribute(data - sort - ${ columnIndex }) || "asc";
    direction = direction === "asc" ? "desc" : "asc";
    table.setAttribute(data - sort - ${ columnIndex }, direction);
    const rows = Array.from(table.rows).slice(1);
    const field = table.rows[0].cells[columnIndex].getAttribute("data-field");
    rows.sort((a, b) => {
        const cellA = a.cells[columnIndex].innerText.toLowerCase();
        const cellB = b.cells[columnIndex].innerText.toLowerCase();
        if (cellA < cellB) return direction === "asc" ? -1 : 1;
        if (cellA > cellB) return direction === "asc" ? 1 : -1;
        return 0;
    });
    const filterField = document.getElementById("filterField").value;
    const filterValue = document.getElementById("filterValue").value.toLowerCase();
    const filteredRows = rows.filter(row => {
        const cellValue = row.cells[table.rows[0].querySelector([data - field=${ filterField }]).cellIndex].innerText.toLowerCase();
        return cellValue.includes(filterValue);
    });
    const userTableBody = document.getElementById("userTableBody");
    userTableBody.innerHTML = "";
    filteredRows.forEach(row => userTableBody.appendChild(row));
    updateSortIcons(columnIndex, direction);
}
function updateSortIcons(columnIndex, direction) {
    const headers = document.querySelectorAll('#userTable th');
    headers.forEach((header, index) => {
        if (index === columnIndex) {
            header.innerHTML = header.getAttribute('data-field').replace('_', ' ') + (direction === "asc" ? ' &uarr;' : ' &darr;');
        } else {
            header.innerHTML = header.getAttribute('data-field').replace('_', ' ') + ' &uarr;&darr;';
        }
    });
}
document.getElementById("filterForm").addEventListener("submit", function (event) {
    event.preventDefault();
    sortAndFilterTable(0);
});