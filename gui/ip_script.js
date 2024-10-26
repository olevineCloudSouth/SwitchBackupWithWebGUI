function track_ip() { 
    const ip_date = document.getElementById('ip_date').value; 
    const ip = document.getElementById('ip_to_track').value;
    const url = `http://127.0.0.1:5000/track_ip?date=${encodeURIComponent(ip_date)}&ip=${encodeURIComponent(ip)}`;
    console.log(url)
    fetch(url, { 
        method: 'GET', 
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())  // Parse JSON response
    .then(data => {
        const resultsList = document.getElementById('resultsList');
        resultsList.innerHTML = '';  // Clear previous results

        // Populate list with each result item
        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `Subnet: ${item.subnet} <br>In Switch: ${item.switch_name} <br>In VLAN: ${item.vlan}`;
            resultsList.appendChild(listItem);
        });
    })
    .catch(error => console.error('Error fetching config:', error));
}
document.addEventListener('DOMContentLoaded', function() { 
    const ip_date = document.getElementById('ip_date'); 
    const ip = document.getElementById('ip_to_track');
    const ip_track_button = document.getElementById('ip_track');

    function validateDateFormat(date) {
        const regex = /^(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1])-\d{4}$/; return regex.test(date) || 
        date.toLowerCase() == 'current';
    }
    function validateIpFormat(ip) {
        const regex = /^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/;
        return regex.test(ip);
    }
    function updateButtonState() { if (validateDateFormat(ip_date.value) && validateIpFormat(ip.value)) { 
            ip_track_button.disabled = false; ip_track_button.disabled = false; 
            ip_track_button.style.backgroundColor = '#4CAF50';
        } else {
            ip_track_button.disabled = true; ip_track_button.disabled = true; 
            ip_track_button.style.backgroundColor = 'grey';
        }
    }
    ip_date.addEventListener('input', updateButtonState); ip_to_track.addEventListener('input', updateButtonState);
    // Initialize button state
    updateButtonState();
});