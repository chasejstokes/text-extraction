import os
import requests
import base64

# Function to download a file from a URL
def download_file(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

# Function to get the list of files using GitHub API
def get_file_list(owner, repo, path):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print(f"Error accessing GitHub API: {response.status_code}")
        return []
    
    files_data = response.json()
    file_list = []
    
    for file in files_data:
        if file['name'].endswith('.png'):
            file_list.append(file['download_url'])
    
    return file_list

# Directory to save the downloaded files
save_dir = 'downloaded_images'
os.makedirs(save_dir, exist_ok=True)

# Repository details
owner = "vis-nlp"
repo = "ChartQA"
path = "ChartQA Dataset/test/png"

# Get the list of files and download each one
file_list = get_file_list(owner, repo, path)

if not file_list:
    print("No files found or error occurred")
else:
    print(f"Found {len(file_list)} files")
    for file_url in file_list:
        file_name = os.path.basename(file_url)
        save_path = os.path.join(save_dir, file_name)
        try:
            download_file(file_url, save_path)
            print(f'Downloaded {file_name}')
        except Exception as e:
            print(f'Error downloading {file_name}: {str(e)}')