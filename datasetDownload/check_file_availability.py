
import requests

def check_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            print(f"{url} is accessible.")
        elif response.status_code == 404:
            print(f"{url} returned a 404 error (Not Found).")
        elif response.status_code == 302:
            print(f"{url} redirected. File might be accessible if you follow the redirect.")
        else:
            print(f"{url} returned status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")

# List of URLs to check
urls = [
    "https://github.com/microsoft/VisEval/blob/main/viseval_dataset.zip"
]

for url in urls:
    check_url(url)
