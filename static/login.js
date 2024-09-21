document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const response = await fetch("/login", {
        method: "POST",
        body: formData
    });
    if (response.redirected) {
        window.location.href = response.url;
    } else {
        const result = await response.json();
        const messageDiv = document.getElementById("message");
        if (response.ok) {
            messageDiv.textContent = result.message;
            messageDiv.style.color = "green";
        } else {
            messageDiv.textContent = result.detail;
            messageDiv.style.color = "red";
        }
    }
});
