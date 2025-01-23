function formatDate(dateStr) {
    const dateParts = dateStr.split('-'); // dateStr is in yyyy-mm-dd format
    const year = dateParts[0];
    let month = dateParts[1];
    let day = dateParts[2];
    
    // Ensure the month and day are in two digits
    month = month.padStart(2, '0');
    day = day.padStart(2, '0');

    return month + '-' + day + '-' + year;
}

function track_ip() { 
    const ip_date = document.getElementById('ip_date').value;
    //format date input
    ip_date = formatDate(ip_date)
    const ip = document.getElementById('ip_to_track').value;
    const url = `/api/track_ip?date=${encodeURIComponent(ip_date)}&ip=${encodeURIComponent(ip)}`;
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
	if (data.length == 0){
		const listItem = document.createElement('li');
		listItem.innerHTML = `That IP does not seem to be routed in the switch configs from this date.`;
		resultsList.appendChild(listItem);

	}
    })
    .catch(error => console.error('Error fetching config:', error));
}


document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('ip_date');
    const ipInput = document.getElementById('ip_to_track');
    const trackButton = document.getElementById('ip_track');

    // Function to check if inputs are filled
    function toggleButtonState() {
        if (dateInput.value && ipInput.value) {
            trackButton.disabled = false;
        } else {
            trackButton.disabled = true;
        }
    }

    // Attach event listeners to the inputs
    dateInput.addEventListener('input', toggleButtonState);
    ipInput.addEventListener('input', toggleButtonState);

    // Disable the button initially
    trackButton.disabled = true;
});