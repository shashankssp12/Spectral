
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from share.views import protected_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('share.urls')),  # For API views
    path('', include('share.urls')),  # For template views
    path('protected-media/<path:file_path>', protected_media, name='protected_media'),
]

# Only serve media files directly in development for non-protected files
# Protected files go through our protected_media view
if settings.DEBUG:
    # Remove direct media serving to force all through protected view
    pass
