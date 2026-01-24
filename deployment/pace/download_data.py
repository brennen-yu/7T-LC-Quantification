"""
Robust data downloader for AHEAD dataset using Figshare API.
Automatically fetches all files associated with the AHEAD dataset article (ID: 10007840).

Usage: python3 download_data.py
"""

import os
import sys
import json
import urllib.request
from pathlib import Path

# AHEAD Dataset Article ID (from DOI 10.21942/uva.10007840)
ARTICLE_ID = 10007840
BASE_URL = "https://api.figshare.com/v2"

def get_project_root():
    return Path(__file__).resolve().parent.parent.parent

def get_file_list(article_id):
    """Fetch list of files from Figshare Article API."""
    url = f"{BASE_URL}/articles/{article_id}/files"
    print(f"Fetching metadata from: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"[Error] Failed to fetch article metadata: {e}")
        sys.exit(1)

def download_file(file_info, dest_dir):
    """Download a single file using its metadata."""
    filename = file_info['name']
    download_url = file_info['download_url']
    dest_path = dest_dir / filename
    
    if dest_path.exists():
        # Optional: Check size match? file_info['size']
        print(f"[Skip] {filename} exists.")
        return

    print(f"[Download] {filename} ({file_info['size'] / 1e9:.2f} GB)...")
    
    try:
        def reporthook(blocknum, blocksize, totalsize):
            readso_far = blocknum * blocksize
            if totalsize > 0:
                percent = readso_far * 1e2 / totalsize
                s = "\r%5.1f%% %*d / %d" % (
                    percent, len(str(totalsize)), readso_far, totalsize)
                sys.stderr.write(s)
                if readso_far >= totalsize:
                    sys.stderr.write("\n")
        
        urllib.request.urlretrieve(download_url, dest_path, reporthook=reporthook)
        print("[OK]")
        
    except Exception as e:
        print(f"[FAILED] {filename}: {e}")

def main():
    root = get_project_root()
    download_dir = root / "data" / "AHEAD_dataset_download"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Target Directory: {download_dir}")
    
    # 1. Get List
    files = get_file_list(ARTICLE_ID)
    print(f"Found {len(files)} files.")
    
    # 2. Download
    for f in files:
        download_file(f, download_dir)
        
    print("\n------------------------------------------------")
    print("Download Complete.")
    print("Next Steps:")
    print(f"cd {download_dir}")
    print("tar -xzf Part1.tar.gz")
    print("tar -xzf Part2.tar.gz")
    print("------------------------------------------------")

if __name__ == "__main__":
    main()
