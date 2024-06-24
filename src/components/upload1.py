from split import DocumentSplitter
from embedding import embedding_model
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from src.components.doc_loader import Process_resume

azure_connection_string = "DefaultEndpointsProtocol=https;AccountName=resumeaibotcontainer;AccountKey=HqvtaWTI+6q17HtNKrYtq0D7nHmWSCmi8TLQbNLJ9j4j9tQN3EZF2ggKO6sF0S6hPA8gZsg0C3Lh+ASt/gc17A==;EndpointSuffix=core.windows.net"
container_name = "resumeaiblobcontainter" 

# Define paths
resumes_path = "/home/akanksha/Documents/Resume_AI 10/downloaded_resumes1"
#vectordb_path = "/home/akanksha/Documents/Resume_AI 10/Vector_db1"
csv_file_path = "/home/akanksha/Documents/Resume_AI 10/appli.csv"
output_folder = "/home/akanksha/Documents/Resume_AI 10/downloaded_resumes1"


class ProcessResume:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def start_loading(self, output_folder):
        load_docs= Process_resume(csv_file_path)
        documents = load_docs.start_loading(output_folder)
        return documents
        
class LoadResumes:
    def __init__(self, input_folder, azure_connection_string, container_name):
        self.input_folder = input_folder
        self.blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        self.container_name = container_name

    def process_docs(self, documents):
        for document in documents:
            content = document.page_content
            blob_name = document.metadata
            self.upload_to_azure(content, blob_name)

    def upload_to_azure(self, content, blob_name):
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            blob_client.upload_blob(content, overwrite=True)
            print(f"Uploaded to Azure: {blob_name}")
        except Exception as e:
            print(f"Error uploading to Azure: {e}")
    
# Initialize and process documents
loader = LoadResumes(resumes_path, azure_connection_string, container_name)
loader.process_docs()
