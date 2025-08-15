from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView, UserProfileView, SharedFileView, SharedFileDetailView, SimilarImagesView, StarredFileView,
    # New template views
    index_view, login_view, signup_view, logout_view, dashboard_view, image_search_view, upload_file_view, starred_view, trash_view
)

urlpatterns = [
    # Existing API endpoints
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('shared-files/', SharedFileView.as_view(), name='shared_files'),
    path('shared-files/<int:pk>/', SharedFileView.as_view(), name='shared_file'),
    path('shared-file/<int:pk>/', SharedFileDetailView.as_view(), name='shared_file'),
    path("similar-images/", SimilarImagesView.as_view(), name="similar_images"),
    path('starred-files/<int:file_id>/', StarredFileView.as_view(), name='starred_file'),
    # Template URLs new template routes
        path('', index_view, name='index'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/signup/', signup_view, name='signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('upload/', upload_file_view, name='upload_file'),
    path('image-search/', image_search_view, name='image_search'),
    path('starred/', starred_view, name='starred'),
    path('trash/', trash_view, name='trash'),
]
