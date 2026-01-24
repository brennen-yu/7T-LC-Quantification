#!/bin/bash
# Script to download and prep AHEAD data on PACE
# Usage: bash download_and_prep_data.sh

set -e # Exit on error

# Directory Setup
PROJECT_ROOT=$(pwd)
DOWNLOAD_DIR="$PROJECT_ROOT/data/AHEAD_dataset_download"
BIDS_DIR="$PROJECT_ROOT/data/bids_input"

echo "Setting up directories..."
mkdir -p "$DOWNLOAD_DIR"
mkdir -p "$BIDS_DIR"

cd "$DOWNLOAD_DIR"

# 1. Download
echo "------------------------------------------------"
echo "Starting Downloads..."
echo "------------------------------------------------"

# Function to download
download_file() {
    local url=$1
    local filename=$2
    if [ -f "$filename" ]; then
        echo "$filename already exists, skipping."
    else
        echo "Downloading $filename..."
        # Use curl with location following (-L) and retry (-C -)
        curl -L -C - -o "$filename" "$url"
    fi
}

# Mapping based on user input
download_file "https://uvaauas.figshare.com/ndownloader/files/21204912" "Part1.tar.gz"
download_file "https://uvaauas.figshare.com/ndownloader/files/21205128" "Part2.tar.gz"
download_file "https://uvaauas.figshare.com/ndownloader/files/20125841" "participants.csv"
download_file "https://uvaauas.figshare.com/ndownloader/files/21209229" "Structures_mni09b.tar.gz"
download_file "https://uvaauas.figshare.com/ndownloader/files/21209235" "Templates_mni09b.tar.gz"
download_file "https://uvaauas.figshare.com/ndownloader/files/21209274" "Readme.txt"

# 2. Extract
echo "------------------------------------------------"
echo "Extracting data..."
echo "------------------------------------------------"

# Create a temporary extraction folder to inspect structure
EXTRACT_DIR="$DOWNLOAD_DIR/extracted_temp"
mkdir -p "$EXTRACT_DIR"

# Extract Part 1 and Part 2 (The Images)
for tarball in Part1.tar.gz Part2.tar.gz; do
    echo "Extracting $tarball..."
    tar -xzf "$tarball" -C "$EXTRACT_DIR"
done

echo "------------------------------------------------"
echo "Download and Extraction Complete."
echo "------------------------------------------------"
echo "Files are located in: $EXTRACT_DIR"
echo "Structure check (first 20 lines):"
ls -R "$EXTRACT_DIR" | head -n 20

echo ""
echo "NEXT STEPS:"
echo "1. Verify the structure inside $EXTRACT_DIR matches 'sub-XXXX/ses-1/anat/'"
echo "2. If correct, move the subject folders to $BIDS_DIR:"
echo "   mv $EXTRACT_DIR/sub-* $BIDS_DIR/"
echo "   cp participants.csv $BIDS_DIR/"
echo "   cp Readme.txt $BIDS_DIR/"