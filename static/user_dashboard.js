document.addEventListener("DOMContentLoaded", async function() {
    const container = document.querySelector(".container");
    const loadingMessage = document.createElement("p");
    loadingMessage.textContent = "Loading tickets...";
    container.appendChild(loadingMessage);

    try {
        const response = await fetch("/tickets_user?user_id=18");  // Replace YOUR_USER_ID with the actual user ID from backend
        if (!response.ok) throw new Error('Network response was not ok');
        const tickets = await response.json();

        tickets.forEach(ticket => {
            const ticketDiv = document.createElement("div");
            ticketDiv.classList.add("ticket");
            ticketDiv.draggable = true;
            ticketDiv.id = `ticket-${ticket.id}`;
            ticketDiv.innerHTML = `<strong>${ticket.title}</strong><br>${ticket.description}`;
            document.getElementById(ticket.status.replace(' ', '_')).appendChild(ticketDiv);

            ticketDiv.addEventListener("dragstart", drag);
        });
    } catch (error) {
        console.error('Error fetching tickets:', error);
        // Handle error gracefully
    } finally {
        container.removeChild(loadingMessage);
    }

    function drag(event) {
        event.dataTransfer.setData("text", event.target.id);
    }

    const dropzones = document.querySelectorAll(".dropzone");

    dropzones.forEach(dropzone => {
        dropzone.addEventListener("dragover", function(event) {
            event.preventDefault();
        });
    
        dropzone.addEventListener("drop", async function(event) {
            event.preventDefault();
            const data = event.dataTransfer.getData("text");
            console.log("Dropped ticket ID:", data); // Log the ticket ID being dragged
            const ticketDiv = document.getElementById(data);
            dropzone.appendChild(ticketDiv);
    
            const ticketId = data.split("-")[1];
            const newStatus = dropzone.id.replace('_', ' ');
    
            // Debug log statements to check extracted data
            console.log("Ticket ID:", ticketId);
            console.log("New Status:", newStatus);
    
            try {
                const response = await fetch("/user_update_ticket", {
                    method: "POST",
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({
                        id: ticketId,
                        status: newStatus
                    })
                });
    
                const result = await response.json();  // Parse the response JSON
                console.log("Server response:", result); // Log server response
    
                if (response.ok) {
                    // Display success message to the user
                    alert(result.message);  // Use alert, or customize a message display on the page
                } else {
                    console.error("Error:", result.detail);
                    alert(`Error: ${result.detail}`);  // Display error message if any
                }
            } catch (error) {
                console.error('Error updating ticket status:', error);
                alert('An error occurred while updating the ticket.');
            }
        });
    });
    
    
    
});

document.getElementById("logout").addEventListener("click", async function() {
    const response = await fetch("/logout", { method: "POST" });
    if (response.redirected) {
        window.location.href = response.url;
    } else {
        console.error("Logout failed");
    }
});