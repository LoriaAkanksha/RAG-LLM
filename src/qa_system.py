from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.chat_models import AzureChatOpenAI
from langchain_community.embeddings import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv
import warnings
 
load_dotenv()
embedding_deployement_name = os.getenv("embedding_deployement_name")
llm_deployement_name = os.getenv("llm_deployement_name")
 
warnings.filterwarnings("ignore")
 
 
class QA_System:
    def __init__(self, docs, query):
        self.docs = docs
        self.qa_query = query
    
    def process_job_description_ui(self):
        self.persist_directory = 'temp_vector_db'
        result = None
        if not os.path.exists(self.persist_directory) or not os.listdir(self.persist_directory):
            if not os.path.exists(self.persist_directory):
                os.makedirs(self.persist_directory)
 
            # Create embeddings
            self.embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)
 
            # Create vector database
            self.persist_directory = 'temp_vector_db'
            self.vectordb = Chroma.from_documents(documents=self.docs,
                                                  embedding=self.embeddings,
                                                  persist_directory=self.persist_directory)
            self.vectordb.persist()
            self.vectorstore_retriever = self.vectordb.as_retriever(search_kwargs={"k": 1})
 
            self.turbo_llm = AzureChatOpenAI(deployment_name=llm_deployement_name,
                                             model_name="gpt-35-turbo-16k")
 
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(llm=self.turbo_llm,
                                                        chain_type="stuff",
                                                        retriever=self.vectorstore_retriever,
                                                        return_source_documents=True,
                                                        )
            warning = "If you don't know the answer, just say that you don't know, don't try to make up an answer"
            question = warning + " You are a helpful AI Assistant that follows instructions extremely well to find out the best answer based on the query. Your strength lies in a methodical approach, thinking step by step before providing answers. Find out the best answer according to the Query."
            query = question + self.qa_query
            llm_response = self.qa_chain(query)
            result = llm_response['result']
        else:
            self.embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)
 
            self.vectordb = Chroma(persist_directory=self.persist_directory,
                                   embedding_function=self.embeddings)
            self.vectorstore_retriever = self.vectordb.as_retriever(search_kwargs={"k": 1})
 
            self.turbo_llm = AzureChatOpenAI(deployment_name=llm_deployement_name,
                                             model_name="gpt-35-turbo-16k")
 
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(llm=self.turbo_llm,
                                                        chain_type="stuff",
                                                        retriever=self.vectorstore_retriever,
                                                        return_source_documents=True,
                                                        )
            warning = "If you don't know the answer, just say that you don't know, don't try to make up an answer"
            question = warning + " You are a helpful AI Assistant that follows instructions extremely well to find out the best answer based on the query. Your strength lies in a methodical approach, thinking step by step before providing answers. Find out the best answer according to the Query."
            query = question + self.qa_query
            llm_response = self.qa_chain(query)
            result = llm_response['result']
        return result