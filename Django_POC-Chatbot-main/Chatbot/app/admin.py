from django.contrib import admin

from .models import (
                     FileModel,
                     Extension_Data,
                     VectorDBInformation,
                     BareActsAgentConfiguration,
                     WebsearchAgentConfiguration,
                     ReflexionAgentConfiguration,
                    )




admin.site.register(FileModel)
admin.site.register(Extension_Data)
admin.site.register(VectorDBInformation)
admin.site.register(BareActsAgentConfiguration)
admin.site.register(WebsearchAgentConfiguration)
admin.site.register(ReflexionAgentConfiguration)