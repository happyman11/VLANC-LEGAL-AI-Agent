import os
import ollama
from .utils import *
from .prompts import *
from dotenv import load_dotenv
from google.genai import Client
import google.generativeai as genai
from langchain_community.chat_models import ChatOllama
from .tools_and_schemas import Reflection,SearchQueryList
from langchain_google_genai import ChatGoogleGenerativeAI

class Ai_Models_Reflexion:
    def __init__(self):
        self.model_name = ""
        self.google_model=["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
        self.keys=Get_API_Keys()
        self.genai = genai 
        self.genai.configure(api_key=self.keys.get_Summary_Search_API())

    def get_models(self, model_name: str, prompt: str) -> str:
        self.model_name = model_name
        if self.model_name in self.google_model :
            model = self.genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        else:
            response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt}])
            return response['message']['content'].strip()
        
class Ai_Models_Bare_Acts:
    def __init__(self):
        self.model_name = ""
        self.google_model=["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
        self.keys=Get_API_Keys()
        self.genai = genai 
        self.genai.configure(api_key=self.keys.get_Acts_Search_API())

    def get_models(self, model_name: str, prompt: str) -> str:
        self.model_name = model_name
        if self.model_name in self.google_model:
            model = self.genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        else:
            response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt}])
            return response['message']['content'].strip()
        
        
class Ai_Models_WebSearch:
    def __init__(self):
        self.google_model=["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
        self.model_name =""
        self.keys=Get_API_Keys()
        self.genai_client = Client(api_key=self.keys.get_Web_Search_API())
        

    def get_generate_answers_model(self,model_name:str,formatted_prompt:str):
        self.model_name = model_name
        if self.model_name in self.google_model:
            llm = ChatGoogleGenerativeAI(
                                     model=self.model_name ,
                                     temperature=0,
                                     max_retries=2,
                                     api_key=self.keys.get_Web_Search_API(),
                                    )
            result = llm.invoke(formatted_prompt)
            return result
        else:
            response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": formatted_prompt}])
            print("get_generate_answers_model result",result)
            return response['message']['content'].strip()
            
        
        
    def get_generate_reflection_model(self,model_name:str,formatted_prompt:str):
        self.model_name = model_name
        if self.model_name in self.google_model:
            llm = ChatGoogleGenerativeAI(
                                    model=self.model_name,
                                    temperature=1.0,
                                    max_retries=2,
                                    api_key=self.keys.get_Web_Search_API(),
                                    )
            result = llm.with_structured_output(Reflection).invoke(formatted_prompt)
            return result
        else:
            llm=ChatOllama(
                    model=self.model_name,  
                    temperature=1.0,
                    )
            result = llm.with_structured_output(Reflection).invoke(formatted_prompt)
            return result
            
        
    def get_generate_querry_model(self,model_name:str,formatted_prompt:str,state):
        self.model_name = model_name
        if self.model_name in self.google_model:
            llm = ChatGoogleGenerativeAI(
                                    model=self.model_name,
                                    temperature=1.0,
                                    max_retries=2,
                                    api_key=self.keys.get_Web_Search_API(),
                                    )
            structured_llm = llm.with_structured_output(SearchQueryList)

            current_date = get_current_date()
            formatted_prompt = query_writer_instructions.format(
                                                            current_date=current_date,
                                                            research_topic=get_research_topic(state["messages"]),
                                                            number_queries=state["initial_search_query_count"],
                                                            )
            result = structured_llm.invoke(formatted_prompt)
            return result
        else:
            llm = ChatOllama(
                    model=self.model_name,  
                    temperature=1.0,
                    )
            structured_llm = llm.with_structured_output(SearchQueryList)

            current_date = get_current_date()
            formatted_prompt = query_writer_instructions.format(
                                                            current_date=current_date,
                                                            research_topic=get_research_topic(state["messages"]),
                                                            number_queries=state["initial_search_query_count"],
                                                            )
            result = structured_llm.invoke(formatted_prompt)
            return result
        
    def get_generate_websearch_model(self,model_name:str,formatted_prompt:str):
        self.model_name = model_name
        if self.model_name in self.google_model:
            response = self.genai_client.models.generate_content(
                                                        model=self.model_name,
                                                        contents=formatted_prompt,
                                                        config={
                                                                "tools": [{"google_search": {}}],
                                                                "temperature": 0,
                                                               },
                                                        )
            return response
            