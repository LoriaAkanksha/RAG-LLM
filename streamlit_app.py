import streamlit as st
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.chat_models import AzureChatOpenAI
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain.schema import HumanMessage
from src.qa_system import QA_System
import warnings
import os
from dotenv import load_dotenv
import pandas as pd
import sys

sys.setrecursionlimit(5000)

load_dotenv()
embedding_deployement_name = os.getenv("embedding_deployement_name")
llm_deployement_name = os.getenv("llm_deployement_name")

warnings.filterwarnings("ignore")
char = "/home/samar/Documents/VS_code_Projects/Resume_AI/Resumes_all/"
df = pd.read_csv('resumes_csv_file/applicant.csv')


class StreamlitApp:
    def __init__(self):
        st.image("logo.png", use_column_width=False)
        st.title("InfoStride Resumes AI-Bot")
        self.output_list = []
        self.turbo_llm = None
        self.vectorstore_retriever = None
        self.vectordb = None
        self.docs_temp = None

    def run(self):
        try:
            self.process_job_description()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    def process_job_description(self):
        try:
            job_titles = ['All'] + list(df['job_title'].unique())
            selected_job_titles = st.multiselect('Select Job Titles', job_titles)
    
            if 'All' in selected_job_titles:
                filtered_df = df.copy()
            else:
                filtered_df = df[df['job_title'].isin(selected_job_titles)]
    
            countries = ['All'] + list(filtered_df['country'].unique())
            selected_countries = st.multiselect('Select Countries', countries)
    
            if 'All' in selected_countries:
                st.write("All countries selected.")
                selected_countries = countries[1:]  
            else:
                selected_countries = selected_countries
    
            filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
    
            if not filtered_df.empty:
                if 'All' not in selected_countries:
                    states = ['All'] + list(filtered_df['state'].unique())
                    selected_states = st.multiselect('Select States', states)
    
                    if 'All' in selected_states:
                        st.write("All states selected.")
                        selected_states = states[1:]  
                    else:
                        selected_states = selected_states
                
                    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
    
                # Add filter for cities if countries and states are selected
                if not filtered_df.empty:  
                    cities = ['All'] + list(filtered_df['city'].unique())
                    selected_cities = st.multiselect('Select Cities', cities)
    
                    if 'All' in selected_cities:
                        st.write("All cities selected.")
                        selected_cities = cities[1:]  
                    else:
                        selected_cities = selected_cities
    
                    filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
    
            # Add filter for work authorization
            work_authorizations = ['All'] + list(df['work_authorization'].unique())
            selected_work_authorizations = st.multiselect('Select Work Authorizations', work_authorizations, default=['All'], key='work_authorizations_multiselect')
    
            if 'All' in selected_work_authorizations:
                st.write("All work authorizations selected.")
                selected_work_authorizations = work_authorizations[1:]  # Exclude 'All'
            else:
                selected_work_authorizations = selected_work_authorizations
    
            filtered_df = filtered_df[df['work_authorization'].isin(selected_work_authorizations)]
    
            # Add date range filter
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            if start_date and end_date:
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
                filtered_df = filtered_df[(filtered_df['created_at'] >= start_date) & (filtered_df['created_at'] <= end_date)]
    
            if not filtered_df.empty:
                st.dataframe(filtered_df)
    
            filtered_df['resume_path'] = filtered_df['resume_path'].astype(str)
            filtered_df.loc[:, 'resume_path'] = filtered_df['resume_path'].apply(lambda x: x.split('/')[-1])

            for path in filtered_df['resume_path']:
                self.output_list.append({"source": char + path})
    
            self.output_list = [{"source": d["source"]} for d in self.output_list]
    
            self.process_rag_system()
        except Exception as e:
            st.error(f"An error occurred while processing job description: {str(e)}")

    def process_rag_system(self):
        try:
            self.directory = 'Resumes_all'
            self.persist_directory = 'Vector_db'

            if not os.path.exists(self.persist_directory) or not os.listdir(self.persist_directory):
                if not os.path.exists(self.persist_directory):
                    os.makedirs(self.persist_directory)

                loader = DirectoryLoader(self.directory, show_progress=True)
                documents = loader.load()
                docs = self.split_docs(documents)

                embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)

                vectordb = Chroma.from_documents(documents=docs,
                                                embedding=embeddings,
                                                persist_directory=self.persist_directory)
                vectordb.persist()
            else:
                embeddings = AzureOpenAIEmbeddings(deployment=embedding_deployement_name)
                self.vectordb = Chroma(persist_directory=self.persist_directory,
                                    embedding_function=embeddings)

                self.vectorstore_retriever = self.vectordb.as_retriever(
                    search_kwargs={
                        "k": 5,
                        "filter": {
                            "$or": self.output_list
                        }
                    }
                )

                self.turbo_llm = AzureChatOpenAI(deployment_name=llm_deployement_name,
                                                model_name="gpt-35-turbo-16k")

                job_description = st.text_area("Enter job description:")

                generate_button = st.button("Generate")

                # Initialize session_state
                if "button_state" not in st.session_state:
                    st.session_state.button_state = {"generate": False, "answers": False}

                if generate_button:
                    st.session_state.button_state["generate"] = not st.session_state.button_state["generate"]

                if st.session_state.button_state["generate"]:
                    self.process_llm_response(job_description)

                    qa_query = st.text_area("Enter job Query:")
                    answers_button = st.button("Answers")
                    if answers_button:
                        self.process_answers(self.docs_temp,qa_query)
        except Exception as e:
            st.error(f"An error occurred while processing rag system: {str(e)}")


    def split_docs(self, documents, chunk_size=15500, chunk_overlap=10):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            docs = text_splitter.split_documents(documents)
            return docs
        except Exception as e:
            st.error(f"An error occurred in split doc function: {str(e)}")

    def process_llm_response(self, job_description):
        try:
            if st.session_state.button_state["generate"]:
                warning = "If you don't know the answer, just say that you don't know, don't try to make up an answer"
                question = warning + " You are a helpful AI Assistant that follows instructions extremely well to find out the best resume based on the job requirement. Your strength lies in a methodical approach, thinking step by step before providing answers. Find out the best resume according to the job requirement."
                query = question + " JD = " + job_description

                qa_chain = RetrievalQA.from_chain_type(llm=self.turbo_llm,
                                                    chain_type="stuff",
                                                    retriever=self.vectorstore_retriever,
                                                    return_source_documents=True)

                llm_response = qa_chain(query)
                st.write(llm_response['result'])
                st.write('\n\nSources and Summaries:')
                self.docs_temp = llm_response["source_documents"]
                for source in llm_response["source_documents"]:
                    message = HumanMessage(
                        content=f"Generate a summary for the following text. : {source.page_content}"
                    )
                    summary = self.turbo_llm([message])
                    st.write(f"Source: {source.metadata['source']}")
                    st.write(f"Summary: {summary}")
                st.write('\n\nQuestions Based on Job Description')
                Instruction = HumanMessage(
                    content=f"Generate a 5 Question to be asked in interview according to the following text (Job Description).As a hiring manager conducting interviews for the [Job Title] position, your goal is to find the best fit candidate based on the provided job description. Craft a series of interview questions that are logically structured and comprehensive, covering various aspects of the job requirements and candidate qualifications.Your questions should aim to assess the candidate's skills, experience, knowledge, and suitability for the role, ensuring alignment with the job description and organizational goals. Consider primary skills relevant to the position(job description), and structure your questions in a way that facilitates a thorough evaluation of each candidate.  Also, consider incorporating hypothetical scenarios or case studies to assess the candidate's decision-making and problem-solving capabilities in real-world situations. Make sure that it will not look like AI generated questions:{job_description}")
                question_output = self.turbo_llm([Instruction])
                st.write(f"Questions: {question_output}")
        except Exception as e:
            st.error(f"An error occurred in processing LLM response: {str(e)}")

    def process_answers(self,llm_response, qa_query):
        try:
            qa = QA_System(llm_response, qa_query)
            result = qa.process_job_description_ui()
            st.write(f"Answers: {result}")
        except Exception as e:
            st.error(f"An error occurred while processing answers: {str(e)}")


if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
