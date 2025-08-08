#!/usr/bin/env bash

# Function to get the latest Transmission version from GitHub
get_latest_transmission_version() {
    curl -s GET "https://api.github.com/repos/transmission/transmission/tags?per_page=1" | awk -F'[:,"]' '/"name"/{print $5}'
}

# Function to get the current Transmission version from code/torrentclientfactory.py
get_current_transmission_version() {
    grep -o 'Transmission/[0-9.]*' code/torrentclientfactory.py | cut -d '/' -f 2
}

# Function to format version number to four digits
format_version_number() {
    version=$1
    formatted_version=$(echo $version | tr -d '.')   # Remove dots
    length=${#formatted_version}                     # Get the length of the formatted version
    if [ $length -eq 3 ]; then
        echo "${formatted_version}0"                 # Append zero if length is 3
    else
        echo "$formatted_version"                    # Otherwise, return the formatted version as is
    fi
}

# Check if update is needed
latest_version=$(get_latest_transmission_version)
current_version=$(get_current_transmission_version)

echo "::set-output name=latest_version::$latest_version"
echo "::set-output name=current_version::$current_version"

# Formatting versions for class names
current_class_version=$(echo $current_version | tr -d '.')
latest_class_version=$(echo $latest_version | tr -d '.')

# Formatting peer IDs
current_peer_id=$(format_version_number $current_class_version)
latest_peer_id=$(format_version_number $latest_class_version)

if [ "$latest_version" != "$current_version" ]; then
    echo "An update is available. Current version: $current_version, Latest version: $latest_version"

    # Update README.md
    sed -i "s/Transmission $current_version/Transmission $latest_version/" README.md

    # Update torrentclientfactory.py
    sed -i "s/Transmission\/$current_version/Transmission\/$latest_version/g" code/torrentclientfactory.py
    sed -i "s/-TR${current_peer_id}-/-TR${latest_peer_id}-/g" code/torrentclientfactory.py

    echo "Update completed."
else
    echo "Current version is already up to date."
fi

