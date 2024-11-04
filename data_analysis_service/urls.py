from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('analysis.urls')),  # Incluir las URLs de la aplicación 'analysis'
]
