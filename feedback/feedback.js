document.getElementById("feedbackForm").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    const senderEmail = document.getElementById("sender").value;
    const receiverEmail = document.getElementById("receiver").value;
    const feedback = document.getElementById("feedback").value;
  
    const messageElement = document.getElementById("message");
  
    try {
      const response = await fetch("http://localhost:5001/submit-feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sender_email: senderEmail,
          receiver_email: receiverEmail,
          feedback: feedback,
        }),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        messageElement.textContent = data.message;
        messageElement.style.color = "green";
        document.getElementById("feedbackForm").reset();
      } else {
        messageElement.textContent = data.error || "Failed to submit feedback.";
        messageElement.style.color = "red";
      }
    } catch (error) {
      messageElement.textContent = "An error occurred. Please try again.";
      messageElement.style.color = "red";
    }
  });
  