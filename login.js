document.getElementById("submit").addEventListener("click", async (event) => {
    event.preventDefault(); // Prevent default form submission

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const messageElement = document.getElementById("message");

    try {
        const response = await fetch("https://cpr-csr-managements.onrender.com/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        // Ensure the response is JSON and handle non-OK responses
        if (!response.ok) {
            const errorData = await response.json(); // Parse the error response
            messageElement.textContent = errorData.error || "Login failed!";
            messageElement.style.color = "red";
            return;
        }

        // Parse the JSON response
        const data = await response.json(); // Correctly await response.json()

        // Success: Store user details in localStorage
        localStorage.setItem("name", data.name);
        localStorage.setItem("role", data.role);
        localStorage.setItem("section", data.section);

        // Redirect to home page
        window.location.href = "home.html";
    } catch (error) {
        // Catch and handle any errors
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