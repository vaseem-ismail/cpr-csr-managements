async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");
  
    try {
      const response = await fetch("https://cpr-csr-managements.onrender.com/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        // Store user's details in localStorage
        localStorage.setItem("userName", data.name);
        localStorage.setItem("userEmail", data.email);
        localStorage.setItem("userRole", data.role);
  
        // Redirect to home.html
        window.location.href = "home.html";
      } else {
        // Show error message
        message.textContent = data.error || "Invalid email or password!";
        message.style.color = "red";
      }
    } catch (error) {
      message.textContent = `Error: ${error.message}`;
      message.style.color = "red";
    }
  
    // Prevent form submission
    return false;
  }
  