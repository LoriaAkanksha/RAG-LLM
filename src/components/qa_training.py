from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv
import warnings

load_dotenv()
embedding_deployement_name = os.getenv("embedding_deployement_name")

warnings.filterwarnings("ignore")


class QA_training:
    def __init__(self, docs,temp_vector_db_path):
        self.docs = docs
        self.temp_db = temp_vector_db_path
    
    def create_temp_vectorDB(self):
        try:
            self.persist_directory = self.temp_db
            if not os.path.exists(self.persist_directory):
                    os.makedirs(self.persist_directory)
            
            self.embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)
            # Load vector database
            self.vectordb = Chroma(persist_directory = self.persist_directory,
                                  embedding_function=self.embeddings)

            ids = self.vectordb.get()['ids']
            print(ids)
   
            if ids:
                self.vectordb.delete(ids=ids)
                self.vectordb.persist()
            try:
                self.vectordb = Chroma.from_documents(documents=self.docs,
                                                    embedding=self.embeddings,
                                                    persist_directory = self.persist_directory)
                self.vectordb.persist()
                self.vectordb = None

            except Exception as e:
                print(str(e))
        except Exception as e:
            raise str(e)
