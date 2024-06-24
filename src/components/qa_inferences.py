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


class QA_inferenece:
    def __init__(self, query,temp_vector_db_path):
        self.qa_query = query
        self.temp_db = temp_vector_db_path
    
    def load_temp_vector_db(self):
        try:
            self.persist_directory = self.temp_db
            self.embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)
            self.vectordb = Chroma(persist_directory = self.persist_directory,
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
        except Exception as e:
            print(str(e))
            raise str(e)
