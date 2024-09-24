function updateTime() {
    fetch('/elapsed_time')
        .then(response => response.json())
        .then(data => {
            if (data.elapsed !== null) {
                let seconds = Math.floor(data.elapsed);
                let hours = Math.floor(seconds / 3600);
                let minutes = Math.floor((seconds % 3600) / 60);
                let remaining_seconds = seconds % 60;

                // Format time as HH:MM:SS
                let timeString = String(hours).padStart(2, '0') + ':' +
                                 String(minutes).padStart(2, '0') + ':' +
                                 String(remaining_seconds).padStart(2, '0');

                // Update the displayed time
                document.getElementById('elapsed_time').querySelector('span').innerText = timeString;
            } else {
                document.getElementById('elapsed_time').querySelector('span').innerText = '00:00:00';
            }
        });
}

// Update the time every second
setInterval(updateTime, 1000);
