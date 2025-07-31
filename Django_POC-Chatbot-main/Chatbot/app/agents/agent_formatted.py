import os
import sys
import django
from .EVR import *
from .utils import *
from .states import *
from .prompts import *
from .ai_model import *
from typing import Annotated
from google.genai import Client
from langsmith import traceable
from langgraph.types import Send
from langgraph.graph import StateGraph
from .configuration import Configuration
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END, START
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from .tools_and_schemas import SearchQueryList, Reflection
from app.models import VectorDBInformation

   

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chatbot.settings")
# django.setup()

keys=Get_API_Keys()

os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_API_KEY"] = keys.get_Langgraph_API()
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_API")

genai_client = Client(api_key=keys.get_Web_Search_API())

similar_docs=int(os.getenv("similar_docs"))

model=Ai_Models_Bare_Acts()
model_1=Ai_Models_Reflexion()
model_2=Ai_Models_WebSearch()
Pre_suffix_obj=Prefix_Suffix()


##########################
### STARTS WEB SEARCH AGENTS #####
##########################
class Websearch_Agent:
    def __init__(self):
        self.Get_API=Get_API_Keys()
    
    @traceable(name="generate_query")
    def generate_query(self,state: OverallAgentsState, config: RunnableConfig) -> QueryGenerationState:
        configurable = Configuration.from_runnable_config(config)

        if state.get("initial_search_query_count") is None:
            state["initial_search_query_count"] = configurable.number_of_initial_queries
        

        current_date = get_current_date()
        formatted_prompt = query_writer_instructions.format(
                                                            current_date=current_date,
                                                            research_topic=get_research_topic(state["messages"]),
                                                            number_queries=state["initial_search_query_count"],
                                                            )
        result=model_2.get_generate_querry_model(configurable.query_generator_model,formatted_prompt,state)
        return {"search_query": result.query}
    
    @traceable(name="continue_to_web_research")
    def continue_to_web_research(self,state: QueryGenerationState):
        return [
                Send("web_research", {"search_query": search_query, "id": int(idx)})
                for idx, search_query in enumerate(state["search_query"])
                ]
        
    @traceable(name="web_research")
    def web_research(self,state: WebSearchState, config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        formatted_prompt = web_searcher_instructions.format(
                                                            current_date=get_current_date(),
                                                            research_topic=state["search_query"],
                                                            )

        
        response=model_2.get_generate_websearch_model(configurable.query_generator_model,formatted_prompt)
        resolved_urls = resolve_urls(
                                    response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
                                    )
        citations = get_citations(response, resolved_urls)
        modified_text = insert_citation_markers(response.text, citations)
        sources_gathered = [item for citation in citations for item in citation["segments"]]

        return {
                "sources_gathered": sources_gathered,
                "search_query": [state["search_query"]],
                "web_research_result": [modified_text],
                }
        
    @traceable(name="knowledge_reflexion")
    def reflection(self,state: OverallAgentsState, config: RunnableConfig) -> ReflectionState:
        configurable = Configuration.from_runnable_config(config)
        state["research_loop_count"] = state.get("research_loop_count", 0) + 1
        
        reasoning_model = state.get("reasoning_model", configurable.reflection_model)
        current_date = get_current_date()
        formatted_prompt = reflection_instructions.format(
                                                        current_date=current_date,
                                                        research_topic=get_research_topic(state["messages"]),
                                                        summaries="\n\n---\n\n".join(state["web_research_result"]),
                                                         )
        result=model_2.get_generate_reflection_model(reasoning_model,formatted_prompt)
        return {
                "is_sufficient": result.is_sufficient,
                "knowledge_gap": result.knowledge_gap,
                "follow_up_queries": result.follow_up_queries,
                "research_loop_count": state["research_loop_count"],
                "number_of_ran_queries": len(state["search_query"]),
               }

    @traceable(name="evaluate_research")
    def evaluate_research(self,state: ReflectionState,config: RunnableConfig,) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        max_research_loops = (
                              state.get("max_research_loops")
                              if state.get("max_research_loops") is not None
                              else configurable.max_research_loops
                             )
        if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
            return "finalize_answer"
        else:
            return [
                    Send(
                        "web_research",
                            {
                            "search_query": follow_up_query,
                            "id": state["number_of_ran_queries"] + int(idx),
                            },
                        )
                    for idx, follow_up_query in enumerate(state["follow_up_queries"])
                   ]

    @traceable(name="finalize_answer")
    def finalize_answer(self,state: OverallAgentsState, config: RunnableConfig):
        configurable = Configuration.from_runnable_config(config)
        reasoning_model = state.get("reasoning_model") or configurable.answer_model

        current_date = get_current_date()
        formatted_prompt = answer_instructions.format(
                                                     current_date=current_date,
                                                     research_topic=get_research_topic(state["messages"]),
                                                     summaries="\n---\n\n".join(state["web_research_result"]),
                                                     )
        
        result=model_2.get_generate_answers_model(reasoning_model,formatted_prompt)

        unique_sources = []
        for source in state["sources_gathered"]:
            if source["short_url"] in result.content:
                result.content = result.content.replace(
                                                        source["short_url"], source["value"]
                                                        )
                unique_sources.append(source)

        return {
                "Web_Search_answer": result.content,
                "sources_gathered": unique_sources,
                }


##########################
### ENDs WEB SEARCH AGENTS #####
##########################

##########################
### START IT ACT AGENTS #####
##########################

class IT_Act_Agent:
    def __init__(self):
        self.IT_ACT_DB = VectorDBInformation.objects.get(DB_name=os.getenv("IT_ACT_DB"))
        self.EVR_obj_IT=EVR(model_name=os.getenv("EMB_MODEL"),persist_directory=self.IT_ACT_DB.Path,k=similar_docs,dbtype=self.IT_ACT_DB.Type)
        self.IT_emb=self.EVR_obj_IT.get_embedding()
        self.IT_vectordb=self.EVR_obj_IT.get_vectordb()
        self.IT_retriever=self.EVR_obj_IT.get_retriever()
        self.IT_Template_obj=IT_Act_Prompt_Templates()
        
    @traceable(name="IT_route_question")   
    def IT_route_question(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable= Configuration.from_runnable_config(config)
        prompt = self.IT_Template_obj.get_router_prompt(state["User_question"])
        response = model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        state["route_result_IT"] = "retrieve" if "VECTORSTORE" in response.upper() else "no_answer"
        return state
    
    @traceable(name="IT_retrieve")   
    def IT_retrieve(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["IT_ACT_documents"] = self.IT_retriever.invoke(state["User_question"])
        return state
    
    @traceable(name="IT_grade_documents")
    def IT_grade_documents(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["IT_ACT_documents"]:
            prompt = self.IT_Template_obj.get_grader_prompt(state["User_question"],document=doc.page_content)
            result = model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["IT_ACT_documents"] = filtered_docs
        return state
    
    @traceable(name="IT_Act_generate_answer")
    def IT_Act_generate_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        if not state["IT_ACT_documents"]:
            state["IT_Act_Agent_answer"] = "No relevant documents found."
        else:
            configurable = Configuration.from_runnable_config(config)
            context = "\n\n".join(doc.page_content for doc in state["IT_ACT_documents"])
            prompt = self.IT_Template_obj.get_answer_prompt(context=context, question=state["User_question"])
            response = model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
            state["IT_Act_Agent_answer"] = response
        return state
    
    @traceable(name="IT_no_answer")
    def IT_no_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["IT_Act_Agent_answer"] = "I am unable to answer this question as it is outside my knowledge base."
        return state
        
##########################
### END IT ACT AGENTS #####
##########################

##########################
### START BNS ACT AGENTS #####
##########################

class BNS_Act_Agent:
    def __init__(self):
        self.BNS_ACT_DB = VectorDBInformation.objects.get(DB_name=os.getenv("BNS_ACT_DB"))
        self.EVR_obj_BNS=EVR(model_name=os.getenv("EMB_MODEL"),persist_directory=self.BNS_ACT_DB.Path,k=similar_docs,dbtype=self.BNS_ACT_DB.Type)
        self.BNS_emb=self.EVR_obj_BNS.get_embedding()
        self.BNS_vectordb=self.EVR_obj_BNS.get_vectordb()
        self.BNS_retriever=self.EVR_obj_BNS.get_retriever()
        self.BNS_Template_obj=BNS_Act_Prompt_Templates()
    
    @traceable(name="BNS_route_question")   
    def BNS_route_question(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        prompt = self.BNS_Template_obj.get_router_prompt(state["User_question"])
        response = model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        state["route_result_BNS"] = "retrieve" if "VECTORSTORE" in response.upper() else "no_answer"
        return state
    
    @traceable(name="BNS_retrieve")
    def BNS_retrieve(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BNS_Act_documents"] = self.BNS_retriever.invoke(state["User_question"])
        return state
    
    @traceable(name="BNS_grade_documents")
    def BNS_grade_documents(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["BNS_Act_documents"]:
            prompt = self.BNS_Template_obj.get_grader_prompt(state["User_question"],document=doc.page_content)
            result = model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["BNS_Act_documents"] = filtered_docs
        return state
    
    @traceable(name="BNS_Act_generate_answer")
    def BNS_Act_generate_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        if not state["BNS_Act_documents"]:
            state["BNS_Act_Agent_answer"] = "No relevant documents found."
        else:
            configurable = Configuration.from_runnable_config(config)
            context = "\n\n".join(doc.page_content for doc in state["BNS_Act_documents"])
            prompt = self.BNS_Template_obj.get_answer_prompt(context=context, question=state["User_question"])
            response = model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
            state["BNS_Act_Agent_answer"] = response
        return state
    
    @traceable(name="BNS_no_answer")
    def BNS_no_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BNS_Act_Agent_answer"] = "I am unable to answer this question as it is outside my knowledge base."
        return state
        
        
##########################
###END BNS ACT AGENTS #####
##########################


##########################
### STARTS BSA ACTS AGENTS #####
##########################

class BSA_Act_Agent:
    def __init__(self):
        self.BSA_ACT_DB = VectorDBInformation.objects.get(DB_name=os.getenv("BSA_ACT_DB"))
        self.EVR_obj_BSA=EVR(model_name=os.getenv("EMB_MODEL"),persist_directory=self.BSA_ACT_DB.Path,k=similar_docs,dbtype=self.BSA_ACT_DB.Type)
        self.BSA_emb=self.EVR_obj_BSA.get_embedding()
        self.BSA_vectordb=self.EVR_obj_BSA.get_vectordb()
        self.BSA_retriever=self.EVR_obj_BSA.get_retriever()
        self.BSA_Template_obj=BSA_Act_Prompt_Templates()
    
    @traceable(name="BSA_route_question")   
    def BSA_route_question(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        prompt = self.BSA_Template_obj.get_router_prompt(state["User_question"])
        response = model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        state["route_result_BSA"] = "retrieve" if "VECTORSTORE" in response.upper() else "no_answer"
        return state
    
    @traceable(name="BSA_retrieve")
    def BSA_retrieve(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BSA_Act_documents"] = self.BSA_retriever.invoke(state["User_question"])
        return state
    
    @traceable(name="BSA_grade_documents")
    def BSA_grade_documents(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["BSA_Act_documents"]:
            prompt = self.BSA_Template_obj.get_grader_prompt(state["User_question"],document=doc.page_content)
            result = model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["BSA_Act_documents"] = filtered_docs
        return state
   
    @traceable(name="BSA_Act_generate_answer")
    def BSA_Act_generate_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        if not state["BSA_Act_documents"]:
            state["BSA_Act_Agent_answer"] = "No relevant documents found."
        else:
            configurable = Configuration.from_runnable_config(config)
            context = "\n\n".join(doc.page_content for doc in state["BSA_Act_documents"])
            prompt = self.BSA_Template_obj.get_answer_prompt(context=context, question=state["User_question"])
            response = model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
            state["BSA_Act_Agent_answer"] = response
        return state
    
    @traceable(name="BSA_no_answer")
    def BSA_no_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BSA_Act_Agent_answer"] = "I am unable to answer this question as it is outside my knowledge base."
        return state

##########################
### END BSA ACTS AGENTS #####
##########################  


##########################
### START RREFLEXION ACTS AGENTS #####
##########################  
     

class Reflexion_Agent:
    def __init__(self):
        self.Reflexion_Prompt_obj=Reflexion_Prompt() 
    
    @traceable(name="Bare_Act_Compiled")
    def Bare_Act_Compiled(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        prompt=self.Reflexion_Prompt_obj.get_bare_act_reflexion_prompt(state["IT_Act_Agent_answer"],state["BNS_Act_Agent_answer"],state["BSA_Act_Agent_answer"])
        response=model_1.get_models(model_name=configurable.reflexion_model, prompt=prompt)
        state["Bare_Act_Reflexion_answer"]=response
        state["messages"]=[AIMessage(content=response)]
        return state
    
    @traceable(name="Bare_Web_Compiled")
    def Bare_Web_Compiled(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        prompt=self.Reflexion_Prompt_obj.reflexion_web_bare_act_prompt(state["IT_Act_Agent_answer"],state["BNS_Act_Agent_answer"],state["BSA_Act_Agent_answer"],state["Web_Search_answer"],question=state["User_question"])
        response=model_1.get_models(model_name=configurable.reflexion_model, prompt=prompt)
        state["Web_Bare_Act_Reflexion_answers"]=response
        return state

##########################
### END RREFLEXION ACTS AGENTS #####
########################## 
@traceable(name="identity")
def identity(state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
    state["User_question"]=Pre_suffix_obj.get_prefix()+state["User_question"]+Pre_suffix_obj.get_suffix()
    return state

class LegalGraphBuilder:
    def __init__(self, state_type):
        self.Web_Agent=Websearch_Agent()
        self.IT_Act_Agent=IT_Act_Agent()
        self.BNS_Act_Agent=BNS_Act_Agent()
        self.BSA_Act_Agent=BSA_Act_Agent()
        self.Reflexion_Agent=Reflexion_Agent()
        self.Graph = StateGraph(state_type)
        
    def add_nodes(self):
        self.Graph.add_node("start_router", identity)
        
        #Web Search Nodes
        self.Graph.add_node("generate_query", self.Web_Agent.generate_query)
        self.Graph.add_node("web_research", self.Web_Agent.web_research)
        self.Graph.add_node("reflection", self.Web_Agent.reflection)
        self.Graph.add_node("finalize_answer", self.Web_Agent.finalize_answer)

        # IT Act Nodes
        self.Graph.add_node("IT_route_question", self.IT_Act_Agent.IT_route_question)
        self.Graph.add_node("IT_retrieve", self.IT_Act_Agent.IT_retrieve)
        self.Graph.add_node("IT_grade_documents", self.IT_Act_Agent.IT_grade_documents)
        self.Graph.add_node("IT_Act_generate_answer", self.IT_Act_Agent.IT_Act_generate_answer)
        self.Graph.add_node("IT_no_answer", self.IT_Act_Agent.IT_no_answer)

        # BNS Nodes
        self.Graph.add_node("BNS_route_question", self.BNS_Act_Agent.BNS_route_question)
        self.Graph.add_node("BNS_retrieve", self.BNS_Act_Agent.BNS_retrieve)
        self.Graph.add_node("BNS_grade_documents", self.BNS_Act_Agent.BNS_grade_documents)
        self.Graph.add_node("BNS_Act_generate_answer", self.BNS_Act_Agent.BNS_Act_generate_answer)
        self.Graph.add_node("BNS_no_answer", self.BNS_Act_Agent.BNS_no_answer)

        # BSA Nodes
        self.Graph.add_node("BSA_route_question", self.BSA_Act_Agent.BSA_route_question)
        self.Graph.add_node("BSA_retrieve", self.BSA_Act_Agent.BSA_retrieve)
        self.Graph.add_node("BSA_grade_documents", self.BSA_Act_Agent.BSA_grade_documents)
        self.Graph.add_node("BSA_Act_generate_answer", self.BSA_Act_Agent.BSA_Act_generate_answer)
        self.Graph.add_node("BSA_no_answer", self.BSA_Act_Agent.BSA_no_answer)

        # Final Synthesis Node
        self.Graph.add_node("Bare_Act_Compiled", self.Reflexion_Agent.Bare_Act_Compiled)
        # self.Graph.add_node("Bare_Web_Compiled",self.Reflexion_Agent.Bare_Web_Compiled)

    def add_edges(self):
        # Entry
        self.Graph.set_entry_point("start_router")
        
        #Web Search Edges
        self.Graph.add_edge("start_router", "generate_query")
        self.Graph.add_conditional_edges(
                                        "generate_query", self.Web_Agent.continue_to_web_research, ["web_research"]
                                        )

        self.Graph.add_edge("web_research", "reflection")
        self.Graph.add_conditional_edges(
                                        "reflection", self.Web_Agent.evaluate_research, 
                                        ["web_research", "finalize_answer"]
                                        )
        
        self.Graph.add_edge("finalize_answer", END)

        # IT Act flow Web Search Edges
        self.Graph.add_edge("start_router", "IT_route_question")
        self.Graph.add_conditional_edges(
            "IT_route_question",
            lambda state: state["route_result_IT"],
            {
                "retrieve": "IT_retrieve",
                "no_answer": "IT_no_answer"
            }
        )
        self.Graph.add_edge("IT_retrieve", "IT_grade_documents")
        self.Graph.add_edge("IT_grade_documents", "IT_Act_generate_answer")
        self.Graph.add_edge("IT_Act_generate_answer", "BNS_route_question")
        self.Graph.add_edge("IT_no_answer", "BNS_route_question")

        # BNS flow Web Search Edges
        self.Graph.add_conditional_edges(
            "BNS_route_question",
            lambda state: state["route_result_BNS"],
            {
                "retrieve": "BNS_retrieve",
                "no_answer": "BNS_no_answer"
            }
        )
        self.Graph.add_edge("BNS_retrieve", "BNS_grade_documents")
        self.Graph.add_edge("BNS_grade_documents", "BNS_Act_generate_answer")
        self.Graph.add_edge("BNS_Act_generate_answer", "BSA_route_question")
        self.Graph.add_edge("BNS_no_answer", "BSA_route_question")

        # BSA flow Web Search Edges
        self.Graph.add_conditional_edges(
            "BSA_route_question",
            lambda state: state["route_result_BSA"],
            {
                "retrieve": "BSA_retrieve",
                "no_answer": "BSA_no_answer"
            }
        )
        self.Graph.add_edge("BSA_retrieve", "BSA_grade_documents")
        self.Graph.add_edge("BSA_grade_documents", "BSA_Act_generate_answer")
        self.Graph.add_edge("BSA_Act_generate_answer", "Bare_Act_Compiled")
        self.Graph.add_edge("BSA_no_answer", "Bare_Act_Compiled")

        # Final BARE ACT Agents Combined  Edges
        self.Graph.add_edge("Bare_Act_Compiled", END)
        # self.Graph.add_edge("Bare_Web_Compiled",END)
        

    def build(self):
        self.add_nodes()
        self.add_edges()
        return self.Graph.compile(name="VLANC Law Agents")



config = RunnableConfig(configurable={"tracing": True}, run_name="VLANC-LEGAL-AGENT")
_graph_builder = LegalGraphBuilder(OverallAgentsState)
_app = _graph_builder.build()
_app = _app.with_config(config)
mermaid_code = _app.get_graph().draw_mermaid()
# with open("legal_graph.md", "w") as f:
#     f.write(f"```mermaid\n{mermaid_code}\n```")



# def call(question):
#     state = {
#         "User_question": question,
#         "messages": question
#     }
#     output = _app.invoke(state)

#     print("\n✅ Legal Answers:\n")
#     print("\n📜 Web Search Answer:\n", output.get("Web_Search_answer", ""))
#     print("\n📜 IT Act Answer:\n", output.get("IT_Act_Agent_answer", ""))
#     print("\n📜 BNS Answer:\n", output.get("BNS_Act_Agent_answer", ""))
#     print("\n📜 BSA Answer:\n", output.get("BSA_Act_Agent_answer", ""))
#     print("\n📜 All in One Answer:\n", output.get("Bare_Act_Reflexion_answer", ""))
#     print("\n📜 All in One WEB + BARE ACTS Answer:\n", output.get("Web_Bare_Act_Reflexion_answers", ""))
#     return output
#call("Mr. A eveteased a young lady and showed vulgar images on phone with actions and comments.")

