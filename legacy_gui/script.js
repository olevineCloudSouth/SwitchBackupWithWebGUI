function getConfigs() { const switchName = document.getElementById('switch').value; const new_date = 
    document.getElementById('date2').value; const old_date = document.getElementById('date1').value;
    
    // Construct URL with query parameters
    const new_url = 
    `/api/get_config?switch_name=${encodeURIComponent(switchName)}&date=${encodeURIComponent(new_date)}`; 
    document.getElementById('configDisplay1').innerText = ""; 
    document.getElementById('configDisplay2').innerText = ""; 
    document.getElementById('getConfigsButton').disabled = true; 
    document.getElementById('getConfigsButton').style.backgroundColor = 'grey'; fetch(new_url, {
        method: 'GET', headers: { 'Content-Type': 'application/json'
        }
    })
    .then(response => response.json()) .then(config => { document.getElementById('configDisplay2').innerText = config 
	document.getElementById('getConfigsButton').disabled = false; 
        document.getElementById('getConfigsButton').style.backgroundColor = '#4CAF50';;
    })
    .catch(error => console.error('Error fetching config:', error)); const old_url = 
    `/api/get_config?switch_name=${encodeURIComponent(switchName)}&date=${encodeURIComponent(old_date)}`;
    
    fetch(old_url, { method: 'GET', headers: { 'Content-Type': 'application/json'
        }
    })
    .then(response => response.json()) .then(config => { document.getElementById('configDisplay1').innerText = 
        config;
    })
    .catch(error => console.error('Error fetching config:', error));
}
function populateSwitches() { fetch('/api/switch_list') .then(response => response.json()) .then(data => { const 
            switchDropdown = document.getElementById('switch'); data.switch_names.forEach(switchName => {
                const option = document.createElement('option'); option.value = switchName; option.textContent = 
                switchName; switchDropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching switches:', error));
}
window.onload = populateSwitches; document.addEventListener('DOMContentLoaded', function() { const date1 = 
    document.getElementById('date1'); const date2 = document.getElementById('date2'); const getConfigsButton = 
    document.getElementById('getConfigsButton'); const compareConfigsButton = 
    document.getElementById('compareConfigsButton'); function validateDateFormat(date) {
        const regex = /^(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1])-\d{4}$/; return regex.test(date) || 
        date.toLowerCase() == 'current';
    }
    function updateButtonState() { if (validateDateFormat(date1.value) && validateDateFormat(date2.value)) { 
            getConfigsButton.disabled = false; compareConfigsButton.disabled = false; 
            getConfigsButton.style.backgroundColor = '#4CAF50'; compareConfigsButton.style.backgroundColor = 
            '#008CBA';
        } else {
            getConfigsButton.disabled = true; compareConfigsButton.disabled = true; 
            getConfigsButton.style.backgroundColor = 'grey'; compareConfigsButton.style.backgroundColor = 
            'grey';
        }
    }
    date1.addEventListener('input', updateButtonState); date2.addEventListener('input', updateButtonState);
    // Initialize button state
    updateButtonState();
});
function compareConfigs() { const switchName = document.getElementById('switch').value; const new_date = 
    document.getElementById('date2').value; const old_date = document.getElementById('date1').value; 
    document.getElementById('compareConfigsButton').disabled = true; 
    document.getElementById('compareConfigsButton').style.backgroundColor = 'grey'; 
    document.getElementById('compareDisplay').innerText = "";
    // Construct URL with query parameters
    const url = 
    `/api/switch_check?switch_name=${encodeURIComponent(switchName)}&new_date=${encodeURIComponent(new_date)}&old_date=${encodeURIComponent(old_date)}`;
    
    fetch(url, { method: 'GET', headers: { 'Content-Type': 'application/json'
        }
    })
    .then(response => response.json()) .then(config => { document.getElementById('compareDisplay').innerText = 
        config; document.getElementById('compareConfigsButton').disabled = false; 
        document.getElementById('compareConfigsButton').style.backgroundColor = '#008CBA';
    })
    .catch(error => console.error('Error fetching config:', error));
}
