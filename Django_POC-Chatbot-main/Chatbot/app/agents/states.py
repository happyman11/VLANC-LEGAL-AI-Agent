
import operator
from typing import TypedDict, List
from langchain.schema import Document
from dataclasses import dataclass, field
from langgraph.graph import add_messages
from typing_extensions import Annotated
from langgraph.channels import LastValue

class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    search_query: list[Query]


class WebSearchState(TypedDict):
    search_query: str
    id: str


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)  # Final report


def merge_max(a: int, b: int) -> int:
    return max(a, b)

def replace(_, b):
    return b

def append(a, b):
    if a is None:
        return b
    return a + b

class OverallAgentsState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    User_question:Annotated[str, replace]
    User_question_IT_ACT: Annotated[str, replace]
    User_question_BNS_ACT: Annotated[str, replace]
    User_question_BSA_ACT: Annotated[str, replace]
    
    BNS_Act_documents: Annotated[list, append]
    BNS_Act_Agent_answer: Annotated[List[str], "accumulate"]
    
    BSA_Act_documents:Annotated[list, append]
    BSA_Act_Agent_answer: Annotated[List[str], "accumulate"]
    
    IT_ACT_documents: Annotated[list, append]
    IT_Act_Agent_answer: Annotated[List[str], "accumulate"]
    
    Bare_Act_Reflexion_answer: str
    Web_Bare_Act_Reflexion_answers:str
    Web_Search_answer:str
    
    route_result_IT:Annotated[str, replace]
    route_result_BSA:Annotated[str, replace]
    route_result_BNS:Annotated[str, replace]
    
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: Annotated[int, merge_max]
    reasoning_model: str
    
    
class OverallAgentsState_IT_Act(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    User_question:Annotated[str, replace]
    User_question_IT_ACT: Annotated[str, replace]
    IT_ACT_documents: Annotated[list, append]
    IT_Act_Agent_answer: Annotated[List[str], "accumulate"]
    route_result_IT:Annotated[str, replace]
    
class OverallAgentsState_BNS_Act(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    User_question:Annotated[str, replace]
    User_question_IT_ACT: Annotated[str, replace]
    BNS_Act_documents: Annotated[list, append]
    BNS_Act_Agent_answer: Annotated[List[str], "accumulate"]
    route_result_IT:Annotated[str, replace]
    
class OverallAgentsState_BSA_Act(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    User_question:Annotated[str, replace]
    User_question_IT_ACT: Annotated[str, replace]
    BSA_Act_documents: Annotated[list, append]
    BSS_Act_Agent_answer: Annotated[List[str], "accumulate"]
    route_result_IT:Annotated[str, replace]
    
class OverallAgentsState_Web_Search(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    User_question:Annotated[str, replace]
    Web_Search_answer:str
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: Annotated[int, merge_max]
    reasoning_model: str
   
    
    
    
    