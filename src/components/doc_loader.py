import os
import requests
import csv
from urllib.parse import urlparse
from langchain_community.document_loaders import DirectoryLoader
from concurrent.futures import ThreadPoolExecutor, as_completed


class Process_resume:
    def __init__(self,csv_file_path):
        self.csv_file_path = csv_file_path

    def download_resume(self, url, folder_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content_type = response.headers.get('content-type')
                filename = os.path.join(folder_path, os.path.basename(urlparse(url).path))

                if 'application/pdf' in content_type or 'application/msword' in content_type or filename.lower().endswith(('.pdf', '.doc', '.docx')):
                    with open(filename, 'wb') as resume_file:
                        resume_file.write(response.content)
                    print(f"Downloaded: {filename}")
                    return True , url  # Indicate successful download
                else:
                    print(f"Skipped: {url}, Unsupported content type or file extension: {content_type}")
                    return False , url  # Indicate download skipped
            else:
                print(f"Failed to download: {url}, Status code: {response.status_code}")
                return False , url  # Indicate download failed
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False , url  # Indicate download failed

    def start_loading(self, output_folder):
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        rows_to_keep = []  # To store indices of rows with successful downloads
        header_row = None 

        with open(self.csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            header_row = reader.fieldnames  
            urls = [(row["resume_path"], row) for row in reader]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.download_resume, url, output_folder) for url, _ in urls]
            for future in as_completed(futures):
                success, url = future.result()
                if success:
                    for url_check, row in urls:
                        if url_check == url:
                            rows_to_keep.append(row)
        
        with open(self.csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header_row)
            writer.writeheader()  
            writer.writerows(rows_to_keep)  
        print('done............')
        
        print("Documents downloaded Successfully----------------------------Document Loading started from Directory")

        self.loader = DirectoryLoader(output_folder, show_progress=True,use_multithreading=True)
        self.documents = self.loader.load()
        for doc in self.documents:
            source_path = doc.metadata['source']
            filename = os.path.basename(source_path)
            doc.metadata['source'] = filename
        
        return self.documents