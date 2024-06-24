import os
import requests
import csv
from urllib.parse import urlparse

csv_file_path = "resumes_csv_file/applicant.csv"
output_folder = "downloaded_resumes"


def download_resume(url, folder_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            filename = os.path.join(folder_path, os.path.basename(urlparse(url).path))

            # Check content type and file extension
            if 'application/pdf' in content_type or 'application/msword' in content_type or filename.lower().endswith(('.pdf', '.doc', '.docx')):
                with open(filename, 'wb') as resume_file:
                    resume_file.write(response.content)
                print(f"Downloaded: {filename}")
            else:
                print(f"Skipped: {url}, Unsupported content type or file extension: {content_type}")
        else:
            print(f"Failed to download: {url}, Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def main(csv_file_path, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            url = row["resume_path"]
            download_resume(url, output_folder)

if __name__ == "__main__":
    main(csv_file_path, output_folder)
