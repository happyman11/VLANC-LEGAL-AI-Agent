import os
import sys
import django
from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from app.models import WebsearchAgentConfiguration,BareActsAgentConfiguration,ReflexionAgentConfiguration

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chatbot.settings")
# django.setup()


def get_latest_websearch_config():
    """Fetch the latest WebsearchAgentConfiguration entry from DB."""
    return WebsearchAgentConfiguration.objects.latest('id')

def get_latest_bareact_config():
    """Fetch the latest BareActsAgentConfiguration entry from DB."""
    return BareActsAgentConfiguration.objects.latest('id')

def get_latest_reflexion_config():
    """Fetch the latest ReflexionAgentConfiguration entry from DB."""
    return ReflexionAgentConfiguration.objects.latest('id')


class Configuration(BaseModel):
    """The configuration for the agent."""
    
    
    bare_act_router_model: str = Field(
        default_factory=lambda: get_latest_bareact_config().Router_Model,
        description="The name of the language model to use for routing i.e., related to BNS, BSA and IT Act 2000"
    )
    
    bare_act_retriever_model: str = Field(
        default_factory=lambda: get_latest_bareact_config().Retriever_Model,
        description="The name of the language model to use for retrieving the related document according to BNS, BSA and IT Act 2000 with respect to user querry"
    )
    
    bare_act_grader_model: str = Field(
        default_factory=lambda: get_latest_bareact_config().Grader_Model,
        description="The name of the language model to use for grading the retrieved document the related document according to BNS, BSA and IT Act 2000 with respect to user querry"
    )
    
    bare_act_answer_model: str = Field(
        default_factory=lambda: get_latest_bareact_config().Answer_Model,
        description="The name of the language model to use for the legal agent's answer"
    )
    
    reflexion_model: str = Field(
        default_factory=lambda: get_latest_reflexion_config().Reflexion_Model,
        description="The name of the language model to use for the combining legal agent's answer"
    )
    
    
    query_generator_model: str = Field(
        default_factory=lambda: get_latest_websearch_config().Querry_Generator_Model,
        description="The name of the language model to use for the agent's query generation."
    )

    reflection_model: str = Field(
        default_factory=lambda: get_latest_reflexion_config().Reflexion_Model,
        description="The name of the language model to use for the agent's reflection."
    )

    answer_model: str = Field(
        default_factory=lambda: get_latest_websearch_config().Answer_Model,
        description="The name of the language model to use for the agent's answer."
    )

    number_of_initial_queries: int = Field(
        default_factory=lambda: get_latest_websearch_config().Initial_Querry,
        description="The number of initial search queries to generate."
    )

    max_research_loops: int = Field(
        default_factory=lambda: get_latest_websearch_config().Max_Research_Loops,
        description="The maximum number of research loops to perform."
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        configurable = config.get("configurable", {}) if config else {}

        raw_values = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        values = {k: v for k, v in raw_values.items() if v is not None}
        return cls(**values)
