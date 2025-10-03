document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("eventForm");
    const modal = document.getElementById("loadingModal"); // loading modal element

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const activity = document.getElementById("eventType").value.trim();
        const startDate = document.getElementById("startDate").value;
        const endDate = document.getElementById("endDate").value;

        if (!activity) {
            alert("Please enter an activity.");
            return;
        }

        if (!startDate || !endDate) {
            alert("Please select both a start and an end date.");
            return;
        }

        if (new Date(startDate) > new Date(endDate)) {
            alert("Start date cannot be after end date.");
            return;
        }

        // Default location fallback if none chosen
        const chosenLocation = JSON.parse(localStorage.getItem("chosenLocation")) || {
            lat: 30.0444,
            lng: 31.2357,
            city: "Cairo"
        };

        try {
            // Show loading modal
            if (modal) modal.style.display = "flex";

            const response = await fetch("/api/weather", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    city: chosenLocation.city,
                    activity: activity,
                    start_date: startDate,
                    end_date: endDate
                })
            });

            if (!response.ok) {
                throw new Error("Server error: " + response.status);
            }

            const data = await response.json();

            // Hide modal
            if (modal) modal.style.display = "none";

            localStorage.setItem("aiResult", JSON.stringify(data));
            window.location.href = "/results";

        } catch (error) {
            console.error("Error:", error);
            if (modal) modal.style.display = "none"; // hide modal on error
            alert("Something went wrong. Please try again later.");
        }
    });
});
