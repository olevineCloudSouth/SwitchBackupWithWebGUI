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

function getDataMain(){
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
    const endpoint = apiEndpoints[dataType]
    if (!endpoint) {
        alert('Invalid data type selected.');
        return;
    }
    getDataButton.disabled = true;
    //clear displays
    document.getElementById('Display1').innerText = "";
    document.getElementById('Display2').innerText = "";

    var old_date = formatDate(date1)

    if (useCurrent2.checked == true){
        var new_date = 'current';
    } else{
        var new_date = formatDate(date2)
    }

    //code to send api request for old date
    const old_url = `/api/${encodeURIComponent(endpoint)}?date=${encodeURIComponent(old_date)}&switch_name=${encodeURIComponent(switchName)}`;
    console.log(old_url)
    fetch(old_url, {method: 'GET', headers: { 'Content-Type': 'application/json'}})
        .then(response => response.json()) 
        .then(outputText => { 
            document.getElementById('Display1').innerText = outputText;
            //re-enable la buttone
            document.getElementById('getDataButton').disabled = false; 
            })
        .catch(error => {
            console.error('Error fetching config:', error)
            //re-enable la buttone
            document.getElementById('getDataButton').disabled = false; 
            });

    //code to send api request for new date
    const new_url = `/api/${encodeURIComponent(endpoint)}?date=${encodeURIComponent(new_date)}&switch_name=${encodeURIComponent(switchName)}`;
    console.log(new_url)
    fetch(new_url, {method: 'GET', headers: { 'Content-Type': 'application/json'}})
        .then(response => response.json()) 
        .then(outputText => { 
            document.getElementById('Display2').innerText = outputText;
            //re-enable la buttone
            document.getElementById('getDataButton').disabled = false; 
            })
        .catch(error => { 
            console.error('Error fetching config:', error);
            //re-enable la buttone
            document.getElementById('getDataButton').disabled = false; 
            });
}

function compareMain(){
    const switchName = document.getElementById('switch').value; 
    const new_date = document.getElementById('date2').value; 
    const old_date = document.getElementById('date1').value; 
    document.getElementById('compareButton').disabled = true; 
    document.getElementById('compareDisplay').innerText = "";

    const dataType = document.getElementById('dataTypeDropdown').value;
    const apiEndpoints = {
        'configs': 'compare_config',
        'interface-statuses': 'compare_int',
        'arp-tables': 'compare_arp',
        'mac-tables': 'compare_mac',
    };
    const endpoint = apiEndpoints[dataType]
    if (!endpoint) {
        alert('Invalid data type selected.');
        return;
    }

    //send api request
    const url = `/api/${encodeURIComponent(endpoint)}?old_date=${encodeURIComponent(old_date)}&new_date=${encodeURIComponent(new_date)}&switch_name=${encodeURIComponent(switchName)}`;
    console.log(url)
    fetch(url, {method: 'GET', headers: { 'Content-Type': 'application/json'}})
        .then(response => response.json()) 
        .then(outputText => { 
            document.getElementById('compareDisplay').innerText = outputText;
            document.getElementById('compareButton').disabled = false;
            })
        .catch(error => console.error('Error fetching config:', error));

    
}

//remove below this line when done everything below here is for testing
function populateSwitches() {
    const switchDropdown = document.getElementById('switch');

    // Example test data
    const testSwitches = [
        "Switch_A", 
        "Switch_B", 
        "Switch_C", 
        "Switch_D", 
        "Switch_E", 
        "Switch_F",
        "Cs-D-Access-23202"
    ];

    testSwitches.forEach(switchName => {
        const option = document.createElement('option');
        option.value = switchName;
        option.textContent = switchName;
        switchDropdown.appendChild(option);
    });
}

// Call the function on page load to populate with test data
window.onload = function () {
    populateSwitches();
};