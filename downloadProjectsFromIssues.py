import os
import json
import requests
import subprocess
from time import sleep

def download_zip(download_url):
    filename = download_url.split('/')[3] + "-" + download_url.split('/')[4] + ".zip"
    # print(f"Downloading: {filename}")
    download_path = os.path.join("/root/dependencySmell/evaluation/actualSmells/allProjects",filename)
    if os.path.isfile(os.path.join(download_path)):
        print(f"File already exists: {filename}")
        return
    try:
        # Use wget to download the file
        subprocess.run(["wget", download_url, "-P", download_path], check=True)
        print(f"Downloaded: {filename}")
        sleep(5)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {filename}: {e}")

def process_json_file(json_file):
    with open(json_file) as f:
        data = json.load(f)
        download_url = data.get('download_url')
        if download_url:
            # print(f"{download_url}")
            download_zip(download_url)
        else:
            print(f"Error: 'download_url' not found in the JSON file: {json_file}")

def search_json_files(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            # print(f"Processing: {file}")
            if file.endswith('repoInfo.json'):
                json_file_path = os.path.join(root, file)
                # print(f"Processing: {json_file_path}")
                process_json_file(json_file_path)

def main():
    # directory_path = input("Enter the directory path: ")
    directory_path = "/root/ResearchData"
    if not os.path.isdir(directory_path):
        print("Error: The given path is not a valid directory.")
        return

    search_json_files(directory_path)

if __name__ == "__main__":
    main()
