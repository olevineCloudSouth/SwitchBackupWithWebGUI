import os
import re
from datetime import datetime, timedelta

# Define the backup directory
backup_dir = "/mnt/sda/switch-backups/"

# Define a regex pattern for the date format xx-xx-xxxx
date_pattern = re.compile(r"^\d{2}-\d{2}-\d{4}$")

# Calculate the cutoff date for two years
two_years_ago = datetime.now() - timedelta(days=2*365)  # Approximately two years

def delete_old_backups(directory):
    try:
        # List all items in the directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Check if the item is a directory and matches the date pattern
            if os.path.isdir(item_path) and date_pattern.match(item):
                # Parse the date from the folder name
                try:
                    folder_date = datetime.strptime(item, "%m-%d-%Y")
                except ValueError:
                    print(f"Skipping {item}: Not a valid date format")
                    continue
                
                # Check if the folder date is older than two years ago
                if folder_date < two_years_ago:
                    print(f"Deleting folder: {item_path}")
                    # Remove the directory and its contents
                    for root, dirs, files in os.walk(item_path, topdown=False):
                        for file in files:
                            os.remove(os.path.join(root, file))
                        for dir in dirs:
                            os.rmdir(os.path.join(root, dir))
                    os.rmdir(item_path)
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
delete_old_backups(backup_dir)
