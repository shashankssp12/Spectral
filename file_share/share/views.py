from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserProfileSerializer, SharedFileSerializer
from .models import SharedFile
import faiss
import numpy as np
from .desc_generator import generate_tag
from .similar_img import search_similar_images
# added while creating template views: 
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Template views : 

# Public pages
def index_view(request):
    return render(request, 'share/index.html')

def login_view(request):
    # Add login logic here if form is submitted
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # You'll need to authenticate with email instead of username
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'share/login.html')

def signup_view(request):
    # Add signup logic here if form is submitted
    if request.method == 'POST':
        # Process the form data and create a new user
        # You could use your UserRegistrationSerializer here
        pass
    return render(request, 'share/signup.html')

# Protected pages - require login
@login_required
def dashboard_view(request):
    # Get user's shared files
    shared_files = request.user.sharedfile_set.all()
    return render(request, 'share/dashboard.html', {'shared_files': shared_files})

@login_required
def image_search_view(request):
    return render(request, 'share/image-search.html')

def logout_view(request):
    logout(request)
    return redirect('index')


#-- Existing code - REST API views -- 

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SharedFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Add the current user as the file owner
            request.data['shared_by'] = request.user.id
            
            # Process file metadata
            file_type = request.data.get('file_type', '').lower()
            file_url = request.data.get('file')
            
            # Create serializer for the file
            serializer = SharedFileSerializer(data=request.data)
            
            if serializer.is_valid():
                # Generate description for images
                if file_type in ['png', 'jpg', 'jpeg', 'webp', 'gif'] and file_url:
                    try:
                        image_tags = generate_tag(file_url)
                        serializer.validated_data['file_description'] = image_tags
                    except Exception as e:
                        # Continue without description if generation fails
                        print(f"Error generating image description: {e}")
                
                # Save the file
                file_obj = serializer.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Get file type filter from query params
        file_type = request.query_params.get('type', 'all')
        
        # Get all files for the current user
        files = request.user.sharedfile_set.all()
        
        # Apply file type filter if specified
        if file_type != 'all':
            if file_type == 'images':
                files = files.filter(file_type__in=['png', 'jpg', 'jpeg', 'webp', 'gif'])
            elif file_type == 'videos':
                files = files.filter(file_type__in=['mp4', 'webm', 'mov', 'avi'])
            elif file_type == 'documents':
                # Exclude images and videos
                files = files.exclude(file_type__in=['png', 'jpg', 'jpeg', 'webp', 'gif', 'mp4', 'webm', 'mov', 'avi'])
        
        # Serialize and return the files
        shared_files = SharedFileSerializer(files, many=True)
        return Response(shared_files.data)

    def put(self, request, pk):
        try:
            shared_file = request.user.sharedfile_set.get(pk=pk)
            
            # Check if this is a description generation request
            if 'generate_description' in request.data and request.data['generate_description']:
                if shared_file.file_type.lower() in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    try:
                        # Generate description for image
                        image_tags = generate_tag(shared_file.file)
                        shared_file.file_description = image_tags
                        shared_file.save()
                        
                        return Response({
                            'id': shared_file.id,
                            'file_description': shared_file.file_description
                        })
                    except Exception as e:
                        print(f"Error generating image description: {e}")
                        return Response({
                            'error': 'Failed to generate description'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({
                        'error': 'Description generation is only supported for images'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Regular update request (e.g., changing privacy)
            serializer = SharedFileSerializer(shared_file, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        try:
            shared_file = request.user.sharedfile_set.get(pk=pk)
            shared_file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class SharedFileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            shared_file = SharedFile.objects.get(pk=pk)

            if shared_file.share_type == 'public':
                return Response(SharedFileSerializer(shared_file).data)

            if shared_file.shared_by == request.user or request.user.email in shared_file.shared_to:
                return Response(SharedFileSerializer(shared_file).data)

            return Response({'error': 'You are not authorized to view this file'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class SimilarImagesView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        query_image_url = request.query_params.get("image_url")
        image_urls = [img.file for img in SharedFile.objects.all()]
        similar_images = search_similar_images(query_image_url, image_urls)

        return Response(similar_images)
