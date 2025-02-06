function populateSwitches() { fetch('/api/switch_list') .then(response => response.json()) .then(data => { const 
            switchDropdown = document.getElementById('switch'); data.switch_names.forEach(switchName => {
                const option = document.createElement('option'); option.value = switchName; option.textContent = 
                switchName; switchDropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching switches:', error));
}
window.onload = populateSwitches; 


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

document.getElementById("sshButton").addEventListener("click", async function() {
    const switchName = document.getElementById("switch").value;

    if (!switchName) {
        alert("Please select a switch first.");
        return;
    }

    const url = `/api/get_switch_ip?switch_name=${encodeURIComponent(switchName)}`;

    try {
        const response = await fetch(url, { method: 'GET', headers: { 'Content-Type': 'application/json' } });
        if (!response.ok) throw new Error("Failed to fetch switch IP");

        const data = await response.json();
        const switchIP = data.ip;

        if (switchIP) {
            window.location.href = `ssh://${switchIP}`;
        } else {
            alert("No IP found for the selected switch.");
        }
    } catch (error) {
        console.error('Error fetching switch IP:', error);
        alert("Error fetching switch IP. Check console for details.");
    }
});

