from flask import jsonify
from src.components.variables import char
import pandas as pd
class filters:
    def __init__(self,df):
        self.df = df
    
    def get_job_titles(self):
        job_titles = ['All'] + [str(title) for title in self.df['job_title'].unique() if pd.notna(title)]
        
        return job_titles
    
    def get_countries_name(self, selected_job_titles):
        if 'All' in selected_job_titles:
            self.filtered_df = self.df.copy()
        else:
            self.filtered_df = self.df[self.df['job_title'].isin(selected_job_titles)]
        self.countries = ['All'] + list(str(country) for country in self.filtered_df['country'].unique() if pd.notna(country))
        return self.countries
    
    def get_states_names(self,selected_countries_names):

        if 'All' in selected_countries_names:
            self.filtered_df

        else:
            self.filtered_df = self.filtered_df[self.filtered_df['country'].isin(selected_countries_names)]
        self.selected_states = ['All'] + list(str(state) for state in self.filtered_df['state'].unique() if pd.notna(state))
        return self.selected_states

    def get_cities_names(self,selected_states_names):

        if 'All' in selected_states_names:
            self.filtered_df
        else:
            self.filtered_df = self.filtered_df[self.filtered_df['state'].isin(selected_states_names)]
        self.selected_cities = ['All'] + [str(cities) for cities in self.filtered_df['city'].unique() if pd.notna(cities)]
        return  self.selected_cities
        
    def get_work_authorization(self,selected_cities_names):
        if 'All' in selected_cities_names:
            self.filtered_df
        else:
            self.filtered_df = self.filtered_df[self.filtered_df['city'].isin(selected_cities_names)]
        self.selected_authorization = ['All'] + [str(autho) for autho in self.filtered_df['work_authorization'].unique() if pd.notna(autho)]
        return self.selected_authorization
        
    def filter_data_authorization(self,selected_authorization):
        if 'All' in selected_authorization:
            self.filtered_df
        else:
            self.filtered_df = self.filtered_df[self.filtered_df['work_authorization'].isin(selected_authorization)]
        return self.filtered_df

    def get_date(self):
        self.df['created_at'] = pd.to_datetime(self.df['created_at'])
        start_date = str(self.df['created_at'].min().date())
        end_date = str(self.df['created_at'].max().date())
        return start_date, end_date
    
    def get_filterd_data(self,start_date, end_date):

        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            self.filtered_df['created_at'] = pd.to_datetime(self.filtered_df['created_at'])
            self.filtered_data = self.filtered_df[(self.filtered_df['created_at'] >= start_date) & (self.filtered_df['created_at'] <= end_date)]
            self.filtered_data.fillna("", inplace=True)
            self.filtered_data_limited = self.filtered_data.head(50)
            self.filtered_jobs = self.filtered_data_limited.to_dict(orient='records')
            return self.filtered_jobs
          
    def get_output_list(self):
        self.output_list = []
        if not self.filtered_data.empty:
            self.filtered_data['resume_path'] = self.filtered_data['resume_path'].astype(str)
            self.filtered_data.loc[:, 'resume_path'] = self.filtered_data['resume_path'].apply(lambda x: x.split('/')[-1])
            for path in self.filtered_data['resume_path']:
                self.output_list.append( char + path)
    
            #self.output_list = [{"source": d["source"]} for d in self.output_list]
            return self.output_list
        
