from doc_loader import Process_resume
from split import DocumentSplitter
from embedding import embedding_model
from dotenv import load_dotenv
load_dotenv()
import os
import warnings
warnings.filterwarnings("ignore")

resumes_path = "/home/akanksha/Documents/Resume_AI 10/downloaded_resumes1"
vectordb_path = "/home/akanksha/Documents/Resume_AI 10/Vector_db1"
embedding_deployement_name = os.getenv("embedding_deployement_name")
csv_file_path = "/home/akanksha/Documents/Resume_AI 10/applicant 3.csv"
output_folder = "/home/akanksha/Documents/Resume_AI 10/downloaded_resumes1"


load_docs= Process_resume(csv_file_path)
documents = load_docs.start_loading(output_folder)

document_splitter = DocumentSplitter(chunk_size=15500, chunk_overlap=100)
splitted_docs = document_splitter.split_docs(documents)


embeddings = embedding_model(vectordb_path,embedding_deployement_name,splitted_docs)
embeddings.start_embedding()
print("Training part completed")
