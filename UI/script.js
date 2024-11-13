document.getElementById("analyze-button").addEventListener("click", function() {
    const url = document.getElementById("channel-url").value;
    
    if (url) {
        fetch(`/analyze-channel?channel_url=${encodeURIComponent(url)}`)
            .then(response => response.json())
            .then(data => {
                if (data.channel_id) {
                    document.getElementById("result-container").innerHTML = `<p>Channel ID: ${data.channel_id}</p>`;
                } else {
                    document.getElementById("result-container").innerHTML = `<p>No channel found. Please check the URL.</p>`;
                }
            })
            .catch(error => {
                document.getElementById("result-container").innerHTML = `<p>Error: ${error}</p>`;
            });
    } else {
        alert("Please enter a valid YouTube video URL.");
    }
});
