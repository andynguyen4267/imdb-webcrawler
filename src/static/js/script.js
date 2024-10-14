document.getElementById("scraperForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const top = document.getElementById("top").value;
    const plot = document.getElementById("plot").value;
    const exportFormat = document.getElementById("export").value;

    // Send the POST request to your Flask server
    const response = await fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            top: top,
            plot: plot,
            export: exportFormat
        }),
    });

    const data = await response.json();

    // Set the chart image if available
    if (data.chart_url) {
        document.getElementById("chart").src = data.chart_url;
        document.getElementById("chart").style.display = "block";  // Ensure the image is visible
    } else {
        document.getElementById("chart").style.display = "none";
    }

    // Set the download link if available
    if (data.download_url) {
        const downloadLink = `<a href="${data.download_url}" download>Download ${exportFormat.toUpperCase()}</a>`;
        document.getElementById("download-link").innerHTML = downloadLink;
    } else {
        document.getElementById("download-link").innerHTML = "";
    }
});
