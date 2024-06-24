from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import csv
import os

# Mocking Process_resume class from src.components.doc_loader
class Process_resume:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def start_loading(self, output_folder):
        documents = []
        try:
            with open(self.csv_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        url = row["resume_path"]  # Ensure this column exists in your CSV
                        # Mocking the document structure
                        document = {
                            'page_content': f"Content of {url}",
                            'metadata': os.path.basename(url)
                        }
                        documents.append(document)
                    except KeyError as e:
                        print(f"KeyError: {e} - The CSV file may be missing a required column.")
        except Exception as e:
            print(f"Error loading CSV: {e}")
        return documents

azure_connection_string = "DefaultEndpo.net"
container_name = "aiblobcontainter"

resumes_path = "/home/akanksha/Documents/Resume_AI 10/appli.csv"
csv_file_path = "/home/akanksha/Documents/Resume_AI 10/appli.csv"
output_folder = "/home/akanksha/Documents/Resume_AI 10/downloaded_resumes1"

class ProcessResume:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def start_loading(self, output_folder):
        load_docs = Process_resume(self.csv_file_path)
        documents = load_docs.start_loading(output_folder)
        return documents

class LoadResumes:
    def __init__(self, input_folder, azure_connection_string, container_name):
        self.input_folder = input_folder
        self.blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        self.container_name = container_name

    def process_docs(self, documents):
        for document in documents:
            content = document['page_content']
            blob_name = document['metadata']
            self.upload_to_azure(content, blob_name)

    def upload_to_azure(self, content, blob_name):
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            blob_client.upload_blob(content, overwrite=True)
            print(f"Uploaded to Azure: {blob_name}")
        except Exception as e:
            print(f"Error uploading to Azure: {e}")

# Execute the process
process_resume = ProcessResume(csv_file_path)
documents = process_resume.start_loading(output_folder)

if documents:
    load_resumes = LoadResumes(resumes_path, azure_connection_string, container_name)
    load_resumes.process_docs(documents)
else:
    print("No documents to process.")
