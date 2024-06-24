from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os


output_folder = 'Output_folder'  
azure_connection_string = "DefaultEndpointsProtocol=https;AccountName=resumeaibotcontainer;AccountKey=HqvtaWTI+6q17HtNKrYtq0D7nHmWSCmi8TLQbNLJ9j4j9tQN3EZF2ggKO6sF0S6hPA8gZsg0C3Lh+ASt/gc17A==;EndpointSuffix=core.windows.net"
container_name = "resumeaiblobcontainter"

class LoadResumes:
    def __init__(self, output_folder, azure_connection_string, container_name, embedding_deployment_name):
        self.output_folder = output_folder
        self.blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        self.container_name = container_name

    
    def upload_to_azure(self, content, blob_name):
            try:
                blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
                blob_client.upload_blob(content, overwrite=True)
                print(f"Uploaded to Azure: {blob_name}")
            except Exception as e:
                print(f"Error uploading to Azure: {e}")