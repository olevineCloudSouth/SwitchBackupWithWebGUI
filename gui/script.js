function getConfigs() {
    const switchName = document.getElementById('switch').value;
    const new_date = document.getElementById('date1').value; 
    const old_date = document.getElementById('date2').value;
    
    // Construct URL with query parameters
    const new_url = `http://127.0.0.1:5000/get_config?switch_name=${encodeURIComponent(switchName)}&date=${encodeURIComponent(new_date)}`;
    
    fetch(new_url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.text())
    .then(config => {
        document.getElementById('configDisplay1').textContent = config;
    })
    .catch(error => console.error('Error fetching config:', error));

    const old_url = `http://127.0.0.1:5000/get_config?switch_name=${encodeURIComponent(switchName)}&date=${encodeURIComponent(old_date)}`;
    
    fetch(old_url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.text())
    .then(config => {
        document.getElementById('configDisplay2').textContent = config;
    })
    .catch(error => console.error('Error fetching config:', error));
}

function populateSwitches() {
    fetch('http://127.0.0.1:5000/switch_list')
        .then(response => response.json())
        .then(data => {
            const switchDropdown = document.getElementById('switch');
            data.switch_names.forEach(switchName => {
                const option = document.createElement('option');
                option.value = switchName;
                option.textContent = switchName;
                switchDropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching switches:', error));
}
window.onload = populateSwitches;