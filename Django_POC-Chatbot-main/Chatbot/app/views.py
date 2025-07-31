import json
from app.apps import agent_app 
from rest_framework import status
from django.utils import timezone
from .agents.agent_formatted import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import *

# @method_decorator(csrf_exempt, name='dispatch')
class Extension_All(APIView):
    def post(self, request):
        user_query = request.data.get("user_input")
        if not user_query:
            return Response({"error": "No user input provided."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            state = {
                    "messages": str(user_query).strip()
                    }
            
            print("User Querry",user_query)
            _app = agent_app["main"]
            output = _app.invoke(state)
            obj_data = Extension_Data(
                                    User_Querry= str(user_query).strip(), 
                                    Web_Search_Answer=output.get("Web_Search_answer", "No Answer"),
                                    IT_Act_Answer=output.get("IT_Act_Agent_answer", "No Answer"),
                                    IT_Act_Document=" ".join(doc.page_content for doc in output.get("IT_ACT_documents", []) if hasattr(doc, 'page_content')) or "No answer",
                                    BNS_Act_Answer=output.get("BNS_Act_Agent_answer", "No Answer"),
                                    BNS_Act_Document=" ".join(doc.page_content for doc in output.get("BNS_Act_documents", []) if hasattr(doc, 'page_content')) or "No answer",
                                    BSA_Act_Answer=output.get("BSA_Act_Agent_answer", "No Answer"),
                                    BSA_Act_Document= " ".join(doc.page_content for doc in output.get("BSA_Act_documents", []) if hasattr(doc, 'page_content')) or "No answer",
                                    Acts_Combined_Answers=output.get("Bare_Act_Reflexion_answer", "No Answer"),
                                    Web_Bare_Act_Combined=output.get("Web_Bare_Act_Reflexion_answers", " No Answer"),
                                    Updated_on=timezone.now()
                                    )
            obj_data.save()

            response_data = {
                            "status": 200,
                            "Web_Search_answer": output.get("Web_Search_answer", ""),
                            "IT_Act_Agent_answer": output.get("IT_Act_Agent_answer", ""),
                            "BNS_Act_Agent_answer": output.get("BNS_Act_Agent_answer", ""),
                            "BSA_Act_Agent_answer": output.get("BSA_Act_Agent_answer", ""),
                            "Bare_Act_Reflexion_answer": output.get("Bare_Act_Reflexion_answer", ""),
                            "Web_Bare_Act_Reflexion_answers": output.get("Web_Bare_Act_Reflexion_answers", "")
                            }
            print("Done")
            return Response(response_data, status=status.HTTP_200_OK)
        
        
