document.getElementById("forgotPasswordForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    try {
        const response = await fetch("/forgot_password", {
            method: "POST",
            body: formData
        });
        const messageDiv = document.getElementById("message");
        if (response.ok) {
            const result = await response.json();
            messageDiv.textContent = result.message;
            messageDiv.style.color = "green";
        } else {
            const result = await response.json();
            messageDiv.textContent = result.detail;
            messageDiv.style.color = "red";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
    }
});
