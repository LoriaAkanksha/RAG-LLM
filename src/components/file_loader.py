from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.document_loaders import AzureBlobStorageFileLoader
from azure.storage.blob import BlobServiceClient
 
class ReadDocsAzure:
    def __init__(self, connection_string, container_name, max_workers=10):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.max_workers = max_workers
 
    def load_document(self, blob_name):
        loader = AzureBlobStorageFileLoader(
            conn_str=self.connection_string,
            container=self.container_name,
            blob_name=blob_name,
        )
        documents = loader.load()
        
        for document in documents:
            if 'source' in document.metadata:
                document.metadata['source'] = document.metadata['source'].split('/')[-1]
        
        return documents
 
    def load_docs(self):
        blob_list = list(self.container_client.list_blobs())
 
        resumes_data = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_blob = {executor.submit(self.load_document, blob.name): blob.name for blob in blob_list}
 
            for future in as_completed(future_to_blob):
                try:
                    print("done")
                    documents = future.result()
                    resumes_data.extend(documents)
                except Exception as exc:
                    print(f'Blob {future_to_blob[future]} generated an exception: {exc}')
 
        return resumes_data