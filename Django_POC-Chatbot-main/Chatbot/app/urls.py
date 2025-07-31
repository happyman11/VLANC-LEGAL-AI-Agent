# urls.py
from django.urls import path
from .views import Extension_All

urlpatterns = [
    path("extension/all", Extension_All.as_view(), name="extention-all"),
    
]
