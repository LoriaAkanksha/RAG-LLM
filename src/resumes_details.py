import os
import requests
import csv
from urllib.parse import urlparse

csv_file_path = "/home/akanksha/Desktop/Resume_AI_Recent/applicant_final.csv"
output_folder = "/home/akanksha/Desktop/Resume_AI_Recent/downloaded_resumes"


def download_resume(url, folder_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            filename = os.path.join(folder_path, os.path.basename(urlparse(url).path))

            if 'application/pdf' in content_type or 'application/msword' in content_type or filename.lower().endswith(('.pdf', '.doc', '.docx')):
                with open(filename, 'wb') as resume_file:
                    resume_file.write(response.content)
                print(f"Downloaded: {filename}")
                return True  # Indicate successful download
            else:
                print(f"Skipped: {url}, Unsupported content type or file extension: {content_type}")
                return False  # Indicate download skipped
        else:
            print(f"Failed to download: {url}, Status code: {response.status_code}")
            return False  # Indicate download failed
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False  # Indicate download failed

def main(csv_file_path, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    rows_to_keep = []  # To store indices of rows with successful downloads

    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for index, row in enumerate(reader):
            url = row["resume_path"]
            if download_resume(url, output_folder):
                rows_to_keep.append(index)

    # Rewrite the CSV file with only successful downloads
    with open(csv_file_path, 'r') as csvfile:
        rows = list(csv.reader(csvfile))
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for idx in rows_to_keep:
            writer.writerow(rows[idx])

if __name__ == "__main__":
    main(csv_file_path, output_folder)
