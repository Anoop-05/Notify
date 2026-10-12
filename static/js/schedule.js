document.addEventListener("DOMContentLoaded", function () {
    const scheduleForm = document.getElementById("scheduleForm");

    if (scheduleForm) {
        scheduleForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const name = document.getElementById("name").value.trim();
            const email = document.getElementById("email").value.trim();
            const dateTime = document.getElementById("dateTime").value;
            const message = document.getElementById("message").value.trim();

            if (!name || !email || !dateTime || !message) {
                alert("Please fill in all fields before scheduling.");
                return;
            }

            fetch("/schedule-notification", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    dateTime: dateTime,
                    message: message
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                scheduleForm.reset();
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Failed to schedule notification. Please try again.");
            });
        });
    }
});
