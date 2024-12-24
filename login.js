document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const messageElement = document.getElementById("message");

    try {
        const response = await fetch("https://cpr-csr-managements.onrender.com/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Store user details in localStorage
            localStorage.setItem("name", data.name);
            localStorage.setItem("role", data.role);
            localStorage.setItem("section", data.section);

            // Redirect to home page
            window.location.href = "home.html";
        } else {
            // Show error message
            messageElement.textContent = data.error || "Login failed!";
            messageElement.style.color = "red";
        }
    } catch (error) {
        // Handle fetch error
        messageElement.textContent = `Error: ${error.message}`;
        messageElement.style.color = "red";
    }
});

const togglePassword = document.getElementById("togglePassword");
const passwordField = document.getElementById("password");

if (togglePassword) {
    togglePassword.addEventListener("click", () => {
        const type = passwordField.getAttribute("type") === "password" ? "text" : "password";
        passwordField.setAttribute("type", type);
        togglePassword.classList.toggle("fa-eye-slash");
    });
}




//https://cpr-csr-managements.onrender.com