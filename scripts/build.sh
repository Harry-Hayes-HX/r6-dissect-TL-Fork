#!/bin/sh

# Navigate to the specified directory
cd /etc/TLMRIS

# Check if the directory change was successful
if [ $? -eq 0 ]; then
    # Execute the go build command with sudo
    sudo go build
else
    echo "Failed to change directory to /etc/TLMRIS. The directory may not exist."
fi