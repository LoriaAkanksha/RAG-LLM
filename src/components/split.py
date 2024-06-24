import os
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentSplitter:
    def __init__(self, chunk_size, chunk_overlap ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        
    def split_docs(self, documents):
        try:
            print("Document Splitting Started _---------------------------------------")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            docs = text_splitter.split_documents(documents)
            print("Document Splitting Completed _---------------------------------------")

            return docs
        except Exception as e:
            raise Exception(f"An error occurred in split doc function: {str(e)}")
        
    