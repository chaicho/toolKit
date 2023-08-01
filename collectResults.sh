#!/bin/bash

target_directory="./"
# Define the destination directory where you want to store the files
destination_directory="./collected_results"

# Create the destination directory if it doesn't exist
mkdir -p "$destination_directory"

# Use the find command to locate all DScheckerResult.txt files and copy them to the destination directory
find "$target_directory" -type f -name "DScheckerResult.txt" -exec cp --parents {} "$destination_directory" \;

echo "All DScheckerResult.txt files have been collected and stored in $destination_directory."
