from django.apps import AppConfig
from langgraph.pregel import RunnableConfig
 

agent_app = {}
class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    
    def ready(self):
        from .agents.agent_formatted import LegalGraphBuilder, OverallAgentsState
        
        config = RunnableConfig(configurable={"tracing": True}, run_name="VLANC-LEGAL-AGENT")
        builder = LegalGraphBuilder(OverallAgentsState)
        app = builder.build().with_config(config)
        
        
        global agent_app
        agent_app = {
                    "main": app
                    }
        
    