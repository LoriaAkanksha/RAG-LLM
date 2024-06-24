import os
import csv
import requests
import PyPDF2
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

embedding_deployment_name = os.getenv("embedding_deployement_name")
csv_file_path = '/home/akanksha/Desktop/Resume_AI_Recent/applicant.csv' 
output_folder = 'Output_folder'  
azure_connection_string = "DefaultEndpointsProtocol=https;AccountName=resumeaibotcontainer;AccountKey=HqvtaWTI+6q17HtNKrYtq0D7nHmWSCmi8TLQbNLJ9j4j9tQN3EZF2ggKO6sF0S6hPA8gZsg0C3Lh+ASt/gc17A==;EndpointSuffix=core.windows.net"
container_name = "resumeaiblobcontainter"

class LoadResumesFromExcel:
    def __init__(self, csv_file_path, output_folder, azure_connection_string, container_name, embedding_deployment_name):
        self.csv_file_path = csv_file_path
        self.output_folder = output_folder
        self.blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        self.container_name = container_name
        self.embedding_deployment_name = embedding_deployment_name

    def download_resume(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content_type = response.headers.get('content-type')
                if 'application/pdf' in content_type or 'application/msword' in content_type or url.lower().endswith(('.pdf', '.doc', '.docx')):
                    print(response.content)
                    return response.content
                else:
                    print(f"Skipped: {url}, Unsupported content type or file extension: {content_type}")
                    return None
            else:
                print(f"Failed to download: {url}, Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
        


    '''def upload_to_azure(self, content, blob_name):
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            blob_client.upload_blob(content, overwrite=True)
            print(f"Uploaded to Azure: {blob_name}")
        except Exception as e:
            print(f"Error uploading to Azure: {e}")'''

    def split_docs(self, document, chunk_size=15500, chunk_overlap=100):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            docs = text_splitter.split_documents([document])
            return docs
        except Exception as e:
            print(f"An error occurred in split doc function: {str(e)}")
            return []
        
    def embed_docs(self, documents):
        try:
            embeddings = AzureOpenAIEmbeddings(deployment=self.embedding_deployment_name)
            vectordb = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=self.output_folder)
            vectordb.persist()
            print('Embedding and persisting completed.')
            return vectordb
        except Exception as e:
            print(f"An error occurred during embedding: {str(e)}")
            return None

    def process_resumes(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        rows_to_keep = []

        with open(self.csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader):
                url = row["resume_path"]
                content = self.download_resume(url)
                if content:
                    document = {'content': content, 'metadata': {'source': url.split('/')[-1]}}
                    chunks = self.split_docs(document)
                    if chunks:
                        self.embed_docs(chunks)
                        blob_name = os.path.basename(urlparse(url).path)
                        self.upload_to_azure(content, blob_name)
                        rows_to_keep.append(index)

        with open(self.csv_file_path, 'r') as csvfile:
            rows = list(csv.reader(csvfile))

        with open(self.csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(rows[0])
            for idx in rows_to_keep:
                writer.writerow(rows[idx + 1])


loader = LoadResumesFromExcel(csv_file_path, output_folder, azure_connection_string, container_name, embedding_deployment_name)
loader.process_resumes()


