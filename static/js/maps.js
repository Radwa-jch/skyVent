// static/js/maps.js
let map;
let marker;

function initMap() {
  const savedRegion = JSON.parse(localStorage.getItem("selectedRegion")) || { lat: 30.0444, lng: 31.2357 };

  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: savedRegion.lat, lng: savedRegion.lng },
    zoom: 6,
  });

  marker = new google.maps.Marker({
    position: { lat: savedRegion.lat, lng: savedRegion.lng },
    map: map,
    draggable: false,
  });

  map.addListener("click", (event) => {
    const clickedLat = event.latLng.lat();
    const clickedLng = event.latLng.lng();
    marker.setPosition(event.latLng);
    localStorage.setItem("chosenLocation", JSON.stringify({ lat: clickedLat, lng: clickedLng }));
  });

  document.getElementById("confirmLocationBtn").addEventListener("click", async function () {
    const chosen = JSON.parse(localStorage.getItem("chosenLocation"));
    if (chosen && chosen.lat && chosen.lng) {
      try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${chosen.lat}&lon=${chosen.lng}&format=json`);
        const data = await response.json();
        const city = data.address.city || data.address.town || data.address.village || "Unknown";

        localStorage.setItem("chosenLocation", JSON.stringify({
          lat: chosen.lat,
          lng: chosen.lng,
          city: city
        }));

        window.location.href = "/form"; // Redirect to form page
      } catch (err) {
        alert("Failed to fetch city name. Please try again.");
        console.error(err);
      }
    } else {
      alert("Please select a location first.");
    }
  });
}
