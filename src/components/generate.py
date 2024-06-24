import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import AzureChatOpenAI
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain.schema import HumanMessage
from src.components.variables import vectordb_path, resumes_path
from dotenv import load_dotenv
import pandas as pd
import sys

sys.setrecursionlimit(5000)

load_dotenv()
embedding_deployement_name = os.getenv("embedding_deployement_name")
llm_deployement_name = os.getenv("llm_deployement_name")


class Generate_response:
    def __init__(self,output_list):
        self.output_list = output_list
        
    def split_docs(self, documents, chunk_size=15500, chunk_overlap=100):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            docs = text_splitter.split_documents(documents)
            return docs
        except Exception as e:
            raise (f"An error occurred in split doc function: {str(e)}")
            
    def process_rag_system(self,job_description):
        try:
            self.directory = resumes_path
            self.persist_directory = vectordb_path

            if not os.path.exists(self.persist_directory) or not os.listdir(self.persist_directory):
                if not os.path.exists(self.persist_directory):
                    os.makedirs(self.persist_directory)

                self.loader = DirectoryLoader(self.directory, show_progress=True)
                self.documents = self.loader.load()
                self.docs = self.split_docs(self.documents)

                self.embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)

                vectordb = Chroma.from_documents(documents=self.docs,
                                                embedding=self.embeddings,
                                                persist_directory=self.persist_directory)
                vectordb.persist()
            else:
                self.embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)
                self.vectordb = Chroma(persist_directory=self.persist_directory,
                                    embedding_function=self.embeddings)

                
                self.vectorstore_retriever = self.vectordb.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={
                        "score_threshold" :0.5,
                        "k": 10,
                        "filter": {
                            "source": {"$in": self.output_list}
                        }
                    }
                )

                self.turbo_llm = AzureChatOpenAI(deployment_name=llm_deployement_name,
                                                model_name="gpt-35-turbo-16k")
                docs = self.vectorstore_retriever.get_relevant_documents(job_description)
                self.docs_temp = docs
                #print(self.docs_temp)
                source_summaries = []
            
                for i in range(len(docs)):
                    message = HumanMessage(
                        content=f"Generate a summary for the following text. Start with the Name of Person :{docs[i].page_content}"
                    )
                    summary = self.turbo_llm([message])
                    summary = summary.content
                    source_path = docs[i].metadata['source']
                    source_summaries.append(source_path)
                    source_summaries.append(summary)
                Instruction = HumanMessage(
                    content=f"Generate a 5 Question to be asked in interview according to the following text (Job Description).As a hiring manager conducting interviews for the [Job Title] position, your goal is to find the best fit candidate based on the provided job description. Craft a series of interview questions that are logically structured and comprehensive, covering various aspects of the job requirements and candidate qualifications.Your questions should aim to assess the candidate's skills, experience, knowledge, and suitability for the role, ensuring alignment with the job description and organizational goals. Consider primary skills relevant to the position(job description), and structure your questions in a way that facilitates a thorough evaluation of each candidate.  Also, consider incorporating hypothetical scenarios or case studies to assess the candidate's decision-making and problem-solving capabilities in real-world situations. Make sure that it will not look like AI generated questions:{job_description}")
                question_output = self.turbo_llm([Instruction])
                question_output = question_output.content
                output_dict = {
                        'llm_result': ' ',
                        'sources_summaries': source_summaries,
                        'Questions': [question_output]
                } 
                return output_dict,self.docs_temp
    
        except Exception as e:
            raise (f"An error occurred while processing answers: {str(e)}")
       