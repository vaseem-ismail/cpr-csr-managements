document.getElementById("registerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
  
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const section = document.getElementById("section").value;
    const role = document.getElementById("role").value;
    const message = document.getElementById("message");
  
    try {
      const response = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          password,
          section,
          role,
        }),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        message.textContent = "Registration successful!";
        message.style.color = "green";
        // Optionally clear the form fields
        document.getElementById("registerForm").reset();
      } else {
        message.textContent = data.error || "Registration failed!";
        message.style.color = "red";
      }
    } catch (error) {
      message.textContent = `Error: ${error.message}`;
      message.style.color = "red";
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