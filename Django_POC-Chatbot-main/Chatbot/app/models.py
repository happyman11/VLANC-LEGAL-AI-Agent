
from django.db import models
from django.utils import timezone


class FileModel(models.Model):
    Act_name = models.CharField(max_length=100)  
    updated_on = models.DateTimeField(default=timezone.now)  
    doc = models.FileField(upload_to='media/')  

    def __str__(self):
        return self.Act_name
    


class VectorDBInformation(models.Model):
    Type = models.CharField(max_length=100)  
    Checked_on = models.DateTimeField(default=timezone.now)  
    DB_name = models.CharField(max_length=100)
    Status = models.BooleanField(default=False)  
    Records_count = models.IntegerField(default=0)  
    Path=models.CharField(max_length=1000)


    def __str__(self):
        return f"{self.DB_name} - {self.Type}"



MODEL_CHOICES = [
                        ("gemini-2.0-flash", "GOOGLE>gemini-2.0-flash"),
                        ("gemini-2.5-flash", "GOOGLE>gemini-2.5-flash"),
                        ("gemini-2.5-pro", "GOOGLE>gemini-2.5-pro"),
                        ("gemma3:4b", "OLLAMA>gemma3:4b"),
                        ("llama3.2:latest", "OLLAMA>llama3.2:latest"),
                        ("llama3.2:1b", "OLLAMA>llama3.2:1b"),
                        ("deepseek-r1:latest", "OLLAMA>deepseek-r1:latest"),
                        ("gemma2:2b", "OLLAMA>gemma2:2b"),
                        ("deepseek-r1:1.5b", "OLLAMA>deepseek-r1:1.5b"),
                        ("llama2:chat", "OLLAMA>llama2:chat"),
                        ("llama3.2:latest", "OLLAMA>llama3.2:latest"),
                        ]
    
class BareActsAgentConfiguration(models.Model):
    Model_Name=models.CharField(max_length=50,choices=MODEL_CHOICES, default="gemini-2.0-flash")
    Router_Model=models.CharField(max_length=50,choices=MODEL_CHOICES, default="gemini-2.0-flash")
    Retriever_Model=models.CharField(max_length=50,choices=MODEL_CHOICES, default="gemini-2.0-flash")
    Grader_Model=models.CharField(max_length=50,choices=MODEL_CHOICES, default="gemini-2.5-flash")
    Answer_Model=models.CharField(max_length=50,choices=MODEL_CHOICES, default="gemini-2.5-pro")
    def __str__(self):
        return f"{self.Model_Name}-{self.Router_Model}-{self.Retriever_Model}-{self.Grader_Model}-{self.Answer_Model}"
  
WEB_MODEL_CHOICES = [
                        ("gemini-2.0-flash", "GOOGLE>gemini-2.0-flash"),
                        ("gemini-2.5-flash", "GOOGLE>gemini-2.5-flash"),
                        ("gemini-2.5-pro", "GOOGLE>gemini-2.5-pro"),
                        ("llama2:chat", "OLLAMA>llama2:chat"),
                    ]  
class WebsearchAgentConfiguration(models.Model):
    Querry_Generator_Model=models.CharField(max_length=50,choices=WEB_MODEL_CHOICES, default="gemini-2.0-flash")
    Reflexion_Model=models.CharField(max_length=50,choices=WEB_MODEL_CHOICES, default="gemini-2.5-flash")
    Answer_Model=models.CharField(max_length=50,choices=WEB_MODEL_CHOICES, default="gemini-2.5-pro")
    Initial_Querry=models.SmallIntegerField(default=3)
    Max_Research_Loops=models.SmallIntegerField(default=2)
    def __str__(self):
        return f"{self.Querry_Generator_Model}-{self.Reflexion_Model}-{self.Answer_Model}-{self.Initial_Querry}-{self.Max_Research_Loops}"

class ReflexionAgentConfiguration(models.Model):
    Reflexion_Model=models.CharField(max_length=50,choices=MODEL_CHOICES, default="gemini-2.5-pro")
    def __str__(self):
        return f"{self.Reflexion_Model}"
    

class Extension_Data(models.Model):
    User_Querry=models.TextField()
    Web_Search_Answer=models.TextField()
    IT_Act_Answer=models.TextField()
    IT_Act_Document=models.TextField()
    BNS_Act_Answer=models.TextField()
    BNS_Act_Document=models.TextField()
    BSA_Act_Answer=models.TextField()
    BSA_Act_Document=models.TextField()
    Acts_Combined_Answers=models.TextField()
    Web_Bare_Act_Combined=models.TextField()
    Updated_on = models.DateTimeField(default=timezone.now) 
   
     
    def __str__(self):
        return f"{self.Updated_on}"
    
 
    
    
    


    