document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    const dob = document.getElementById("dob").value;
    const gender = document.getElementById("gender").value;
    const address = document.getElementById("address").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/send-sms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, phone, dob, gender, address, password })
    });

    const result = await response.json();
    
    if (response.status === 200) {
        document.getElementById("successMessage").textContent = result.message;
    } else {
        document.getElementById("successMessage").textContent = "Error sending SMS!";
    }
});
