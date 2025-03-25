from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, UserProfileView, SharedFileView, SharedFileDetailView, SimilarImagesView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('shared-files/', SharedFileView.as_view(), name='shared_files'),
    path('shared-files/<int:pk>/', SharedFileView.as_view(), name='shared_file'),
    path('shared-file/<int:pk>/', SharedFileDetailView.as_view(), name='shared_file'),
    path("similar-images/", SimilarImagesView.as_view(), name="similar_images"),
]