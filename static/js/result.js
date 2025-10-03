// Load AI result from localStorage
const aiResult = JSON.parse(localStorage.getItem("aiResult"));

if (!aiResult || aiResult.error) {
    document.getElementById("summary").innerText = "Error fetching AI weather recommendation.";
} else {
    // Summary
    const summaryEl = document.getElementById("summary");
    summaryEl.innerHTML = `
        <p><b>Activity:</b> ${aiResult.activity}</p>
        <p><b>Best Day:</b> ${aiResult.best_day ? aiResult.best_day : "No suitable day found"}</p>
        <p><b>Date Range Checked:</b> ${aiResult.start_date} to ${aiResult.end_date}</p>
    `;

    // Recommendations
    const recEl = document.getElementById("recommendations");
    if(aiResult.best_day){
        const bestDayWeather = aiResult.daily_weather.find(d => d.recommendations && d.suitable);
        if(bestDayWeather){
            bestDayWeather.recommendations.forEach(r => {
                const p = document.createElement("p");
                p.innerText = "- " + r;
                recEl.appendChild(p);
            });
        }
    } else {
        const p = document.createElement("p");
        p.innerText = "No suitable day found for your activity. Consider indoor activities.";
        recEl.appendChild(p);
    }

    // Alternative dates
    const altEl = document.getElementById("alternatives");
    if(aiResult.alternative_days.length){
        aiResult.alternative_days.forEach(d => {
            const p = document.createElement("p");
            p.innerText = "- " + d;
            altEl.appendChild(p);
        });
    } else {
        altEl.innerText = "No alternative days available";
    }

    // Chart
    const ctx = document.getElementById("forecastChart").getContext("2d");
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: aiResult.chart_data.labels,
            datasets: [
                { label: "Temperature (°C)", data: aiResult.chart_data.temperature, borderColor: "red", fill: false, tension: 0.2 },
                { label: "Rain (mm)", data: aiResult.chart_data.rain, borderColor: "blue", fill: false, tension: 0.2 },
                { label: "Wind (m/s)", data: aiResult.chart_data.wind, borderColor: "green", fill: false, tension: 0.2 },
                { label: "Air Quality (1=Good,2=Moderate,3=Poor)", data: aiResult.chart_data.air_quality, borderColor: "orange", fill: false, tension: 0.2 }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true } }
        }
    });

    // JSON Download
    document.getElementById("downloadJsonBtn").addEventListener("click", () => {
        const blob = new Blob([JSON.stringify(aiResult, null, 2)], {type: 'application/json'});
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "ai_weather.json";
        link.click();
    });

    // CSV Download
    document.getElementById("downloadCsvBtn").addEventListener("click", () => {
        let csvContent = "data:text/csv;charset=utf-8,";
        const headers = ["Day","Temperature (°C)","Rain (mm)","Wind (m/s)","Air Quality","Recommendations"];
        csvContent += headers.join(",") + "\n";

        aiResult.daily_weather.forEach((d,i) => {
            const row = [
                i+1,
                d.T2M,
                d.PRECTOT,
                d.WS10M,
                d.air_quality,
                d.recommendations.join(" | ")
            ];
            csvContent += row.join(",") + "\n";
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.href = encodedUri;
        link.download = "ai_weather.csv";
        link.click();
    });
}
