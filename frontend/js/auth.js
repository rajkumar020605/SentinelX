const API_URL = "http://127.0.0.1:8000";

const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    loginMessage.textContent = "Logging in...";

    try {

        const formData = new URLSearchParams();

        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(
            `${API_URL}/auth/token`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {

            loginMessage.textContent =
                data.detail || "Login failed.";

            return;
        }

        localStorage.setItem(
            "sentinelx_token",
            data.access_token
        );

        loginMessage.textContent =
            "Login successful. Opening dashboard...";

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 500);

    } catch (error) {

        console.error(error);

        loginMessage.textContent =
            "Unable to connect to SentinelX API.";
    }
});