function populateSwitches() { fetch('/api/switch_list') .then(response => response.json()) .then(data => { const 
            switchDropdown = document.getElementById('switch'); data.switch_names.forEach(switchName => {
                const option = document.createElement('option'); option.value = switchName; option.textContent = 
                switchName; switchDropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching switches:', error));
}
window.onload = populateSwitches; 

// Function to enable/disable buttons and handle the second date input
function updateButtonStates() {
    const date1 = document.getElementById('date1');
    const date2 = document.getElementById('date2');
    const useCurrent2 = document.getElementById('useCurrent2');
    const getDataButton = document.getElementById('getDataButton');
    const compareButton = document.getElementById('compareButton');

    // Get today's date in YYYY-MM-DD format
    const today = new Date().toISOString().split('T')[0];

    // Validate dates
    const isDate1Valid = date1.value.trim() !== '' && date1.value <= today;
    const isDate2Valid = useCurrent2.checked 
        ? true 
        : (date2.value.trim() !== '' && date2.value <= today);

    // Ensure date1 is not newer than date2 (or today if checkbox is checked)
    const isOrderValid = useCurrent2.checked 
        ? date1.value <= today 
        : (date1.value <= date2.value);

    // Enable or disable buttons based on all conditions
    const areButtonsEnabled = isDate1Valid && isDate2Valid && isOrderValid;
    getDataButton.disabled = !areButtonsEnabled;
    compareButton.disabled = !areButtonsEnabled;

    // Disable/enable the second date input based on the checkbox
    date2.disabled = useCurrent2.checked;
}
// Add event listeners to update the button states on input changes
document.getElementById('date1').addEventListener('input', updateButtonStates);
document.getElementById('date2').addEventListener('input', updateButtonStates);
document.getElementById('useCurrent2').addEventListener('change', updateButtonStates);

// Initial state check
updateButtonStates();

// Function to filter dropdown options based on search input
function filterSwitchDropdown() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const switchDropdown = document.getElementById('switch');
    const options = switchDropdown.options;

    // Loop through all options in the dropdown
    for (let i = 0; i < options.length; i++) {
        const optionText = options[i].textContent.toLowerCase();

        // Show or hide options based on whether they match the search input
        if (optionText.includes(searchInput)) {
            options[i].style.display = '';
        } else {
            options[i].style.display = 'none';
        }
    }
}

// Add event listener to the search input
document.getElementById('searchInput').addEventListener('input', filterSwitchDropdown);
//copy to clipboard butttons func
function copyToClipboard(outputBoxId) {
    const outputBox = document.getElementById(outputBoxId);

    if (outputBox) {
        // Create a temporary text area element
        const tempTextArea = document.createElement('textarea');
        tempTextArea.value = outputBox.textContent.trim(); // Get the content of the output box
        document.body.appendChild(tempTextArea);

        // Select and copy the text
        tempTextArea.select();
        document.execCommand('copy');

        // Remove the temporary text area
        document.body.removeChild(tempTextArea);

        // Provide user feedback (optional)
        alert('Copied to clipboard!');
    } else {
        console.error(`Output box with ID "${outputBoxId}" not found.`);
    }
}

//function to parse from yyyy-mm-dd to mm-dd-yyyy
function formatDate(dateStr) {
    var dateParts = dateStr.split('-'); // dateStr is in yyyy-mm-dd format
    var year = dateParts[0];
    var month = dateParts[1];
    var day = dateParts[2];
    
    // Ensure the month and day are in two digits
    month = month.padStart(2, '0');
    day = day.padStart(2, '0');

    return month + '-' + day + '-' + year;
}

async function getDataMain() {
    const date1 = document.getElementById('date1').value;
    const date2 = document.getElementById('date2').value;
    const useCurrent2 = document.getElementById('useCurrent2');
    const getDataButton = document.getElementById('getDataButton');
    const switchName = document.getElementById('switch').value;
    const dataType = document.getElementById('dataTypeDropdown').value;
    const apiEndpoints = {
        'configs': 'get_config',
        'interface-statuses': 'get_int_status',
        'arp-tables': 'get_ip_arp',
        'mac-tables': 'get_mac',
    };

    const endpoint = apiEndpoints[dataType];
    if (!endpoint) {
        alert('Invalid data type selected.');
        return;
    }

    getDataButton.disabled = true;

    // Clear displays
    document.getElementById('Display1').innerText = "";
    document.getElementById('Display2').innerText = "";

    const old_date = formatDate(date1);
    const new_date = useCurrent2.checked ? 'current' : formatDate(date2);

    // Define URLs
    const old_url = `/api/${encodeURIComponent(endpoint)}?date=${encodeURIComponent(old_date)}&switch_name=${encodeURIComponent(switchName)}`;
    const new_url = `/api/${encodeURIComponent(endpoint)}?date=${encodeURIComponent(new_date)}&switch_name=${encodeURIComponent(switchName)}`;

    try {
        // Fetch old date data
        console.log(old_url);
        const oldResponse = await fetch(old_url, { method: 'GET', headers: { 'Content-Type': 'application/json' } });
        const oldData = await oldResponse.json();
        document.getElementById('Display1').innerText = oldData;
    } catch (error) {
        console.error('Error fetching config (old date):', error);
    }

    try {
        // Fetch new date data
        console.log(new_url);
        const newResponse = await fetch(new_url, { method: 'GET', headers: { 'Content-Type': 'application/json' } });
        const newData = await newResponse.json();
        document.getElementById('Display2').innerText = newData;
    } catch (error) {
        console.error('Error fetching config (new date):', error);
    } finally {
        // Re-enable the button
        getDataButton.disabled = false;
    }
}

async function compareMain() {
    const switchName = document.getElementById('switch').value; 
    const new_date_unformat = document.getElementById('date2').value; 
    const old_date_unformat = document.getElementById('date1').value; 
    const useCurrent2 = document.getElementById('useCurrent2');
    document.getElementById('compareButton').disabled = true; 
    document.getElementById('compareDisplay').innerText = "";
    const old_date = formatDate(old_date_unformat);
    const new_date = useCurrent2.checked ? 'current' : formatDate(new_date_unformat);
    const dataType = document.getElementById('dataTypeDropdown').value;
    const apiEndpoints = {
        'configs': 'compare_config',
        'interface-statuses': 'compare_int',
        'arp-tables': 'compare_arp',
        'mac-tables': 'compare_mac',
    };
    const endpoint = apiEndpoints[dataType];
    if (!endpoint) {
        alert('Invalid data type selected.');
        return;
    }

    // Send API request
    const url = `/api/${encodeURIComponent(endpoint)}?old_date=${encodeURIComponent(old_date)}&new_date=${encodeURIComponent(new_date)}&switch_name=${encodeURIComponent(switchName)}`;
    console.log(url);
    try {
        const response = await fetch(url, { method: 'GET', headers: { 'Content-Type': 'application/json' } });
        let outputArray = await response.json();
        outputArray = outputArray[0]
        // Process and format the output
        const compareDisplay = document.getElementById('compareDisplay');
        compareDisplay.innerHTML = ""; // Clear previous content

        outputArray.forEach(([status, text]) => {
            const lineElement = document.createElement('div');
            lineElement.textContent = text;

            if (status === 'same') {
                lineElement.style.color = 'grey';
                lineElement.style.paddingLeft = '10px'; // Indent
            } else if (status === 'add') {
                lineElement.style.color = 'green';
                lineElement.style.fontWeight = 'bold';
                lineElement.textContent = `+ ${text}`; // Prefix with "+"
            } else if (status === 'del') {
                lineElement.style.color = 'red';
                lineElement.style.fontWeight = 'bold';
                lineElement.textContent = `- ${text}`; // Prefix with "-"
            }

            compareDisplay.appendChild(lineElement);
        });

    } catch (error) {
        console.error('Error fetching config:', error);
    } finally {
        document.getElementById('compareButton').disabled = false;
    }
}