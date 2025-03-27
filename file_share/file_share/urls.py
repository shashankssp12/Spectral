
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('share.urls')),  # For API views
    path('', include('share.urls')),  # For template views
]
