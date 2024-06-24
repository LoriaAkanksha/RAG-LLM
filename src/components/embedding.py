import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import AzureOpenAIEmbeddings


class embedding_model:
    def __init__(self, resumes_path, vectordb_path, embedding_deployement_name, documents):
        self.resumes_path = resumes_path
        self.vectordb_path = vectordb_path
        self.embedding_deployement_name = embedding_deployement_name
        self.documents = documents

    def start_embedding(self):
        try:
            print("Embedding model started -----------------------------------------------------")
            # Check if the vector database exists and is populated
            if not os.path.exists(self.vectordb_path) or not os.listdir(self.vectordb_path):
                os.makedirs(self.vectordb_path)

                

                # Initialize embeddings
                embeddings = AzureOpenAIEmbeddings(deployment=self.embedding_deployement_name)

                # Store embeddings in vector database
                vectordb = Chroma.from_documents(documents=self.documents, embedding=embeddings, persist_directory=self.vectordb_path)
                vectordb.persist()

                print("embedding done....... ")
            
        except Exception as e:
            raise Exception(f"An error occurred while processing embeddings: {str(e)}")


