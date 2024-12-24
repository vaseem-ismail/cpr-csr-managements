const API_BASE = "https://cpr-csr-managements.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const resetForm = document.getElementById("resetForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;
      const message = document.getElementById("message");

      try {
        const response = await fetch(`${API_BASE}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        if (response.ok) {
          message.textContent = "Login successful!";
          message.style.color = "green";
          localStorage.setItem("userEmail", data.email);
          window.location.href = "home.html"; // Redirect to home page
        } else {
          message.textContent = data.error || "Login failed!";
          message.style.color = "red";
        }
      } catch (error) {
        message.textContent = `Error: ${error.message}`;
        message.style.color = "red";
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const name = document.getElementById("name").value;
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;
      const message = document.getElementById("message");

      try {
        const response = await fetch(`${API_BASE}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password }),
        });

        const data = await response.json();
        if (response.ok) {
          message.textContent = data.message || "Registration successful!";
          message.style.color = "green";
        } else {
          message.textContent = data.error || "Registration failed!";
          message.style.color = "red";
        }
      } catch (error) {
        message.textContent = `Error: ${error.message}`;
        message.style.color = "red";
      }
    });
  }

  if (resetForm) {
    resetForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const email = document.getElementById("email").value;
      const newPassword = document.getElementById("newPassword").value;
      const message = document.getElementById("message");

      try {
        const response = await fetch(`${API_BASE}/reset-password`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, new_password: newPassword }),
        });

        const data = await response.json();
        if (response.ok) {
          message.textContent = data.message || "Password reset successful!";
          message.style.color = "green";
        } else {
          message.textContent = data.error || "Password reset failed!";
          message.style.color = "red";
        }
      } catch (error) {
        message.textContent = `Error: ${error.message}`;
        message.style.color = "red";
      }
    });
  }
});
