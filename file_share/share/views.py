from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserProfileSerializer, SharedFileSerializer
from .models import SharedFile
from .desc_generator import generate_tag
from .similar_img import search_similar_images
# added while creating template views:
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
import os


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
def upload_file_view(request):
    if request.method == 'POST':
        try:
            # Get the uploaded file
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return redirect('dashboard')

            # Extract file information
            file_name = uploaded_file.name
            file_size = f"{uploaded_file.size / 1024:.1f} KB" if uploaded_file.size < 1024*1024 else f"{uploaded_file.size / (1024*1024):.1f} MB"
            file_type = file_name.split('.')[-1].lower() if '.' in file_name else ''
            
            # Create SharedFile object
            shared_file = SharedFile.objects.create(
                shared_by=request.user,
                file=uploaded_file,
                file_name=file_name,
                file_size=file_size,
                file_type=file_type,
                share_type='private'  # Default to private
            )

            # Generate description for images
            if file_type in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                try:
                    # Build full URL for the image
                    file_url = shared_file.get_file_url()
                    if file_url.startswith('/'):
                        # Convert relative URL to absolute URL
                        full_url = request.build_absolute_uri(file_url)
                    else:
                        full_url = file_url
                    
                    image_tags = generate_tag(full_url)
                    shared_file.file_description = image_tags
                    shared_file.save()
                except Exception as e:
                    print(f"Error generating image description: {e}")

            return redirect('dashboard')
        except Exception as e:
            print(f"Error uploading file: {e}")
            return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def dashboard_view(request):
    # Get file type filter from query params
    file_type = request.GET.get('type', 'all')
    
    # Get all files for the current user
    shared_files = request.user.sharedfile_set.all()
    
    # Apply file type filter if specified
    if file_type != 'all':
        if file_type == 'images':
            shared_files = shared_files.filter(file_type__in=['png', 'jpg', 'jpeg', 'webp', 'gif'])
        elif file_type == 'videos':
            shared_files = shared_files.filter(file_type__in=['mp4', 'webm', 'mov', 'avi'])
        elif file_type == 'documents':
            # Exclude images and videos
            shared_files = shared_files.exclude(file_type__in=['png', 'jpg', 'jpeg', 'webp', 'gif', 'mp4', 'webm', 'mov', 'avi'])
    
    return render(request, 'share/dashboard.html', {'shared_files': shared_files})

@login_required
def image_search_view(request):
    return render(request, 'share/image-search.html')

def logout_view(request):
    logout(request)
    return redirect('index')


def protected_media(request, file_path):
    """
    Serve media files with permission checking
    """
    # Get the file from database
    try:
        # Try to find the file by matching the file path
        shared_file = SharedFile.objects.filter(file__icontains=file_path).first()
        
        if not shared_file:
            # Try to find by exact file name
            filename = os.path.basename(file_path)
            shared_file = SharedFile.objects.filter(file__icontains=filename).first()
        
        if not shared_file:
            raise Http404("File not found in database")
        
        # Check permissions
        if shared_file.share_type == 'public':
            # Public files can be accessed by anyone
            pass
        elif shared_file.share_type == 'private':
            # Private files require authentication and ownership
            if not request.user.is_authenticated:
                return HttpResponse('Unauthorized - Please log in to view this file', status=401)
            
            # Check if user owns the file or is in shared_to list
            if (shared_file.shared_by != request.user and 
                request.user.email not in shared_file.shared_to):
                return HttpResponse('Forbidden - You do not have permission to view this file', status=403)
        
        # Serve the file
        file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(file_full_path):
            # Determine content type based on file extension
            import mimetypes
            content_type, _ = mimetypes.guess_type(file_full_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            return FileResponse(
                open(file_full_path, 'rb'),
                content_type=content_type,
                filename=os.path.basename(file_path)
            )
        else:
            raise Http404("Physical file not found")
            
    except Exception as e:
        print(f"Error in protected_media: {e}")
        return HttpResponse(f'Error: {str(e)}', status=500)


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

            # Check if this is a file upload or URL submission
            uploaded_file = request.FILES.get('file')
            file_url = request.data.get('file_url')
            
            if uploaded_file:
                # Handle file upload
                file_name = uploaded_file.name
                file_size = f"{uploaded_file.size / 1024:.1f} KB" if uploaded_file.size < 1024*1024 else f"{uploaded_file.size / (1024*1024):.1f} MB"
                file_type = file_name.split('.')[-1].lower() if '.' in file_name else ''
                
                request.data['file_name'] = file_name
                request.data['file_size'] = file_size
                request.data['file_type'] = file_type
                
            elif file_url:
                # Handle URL submission
                file_name = request.data.get('file_name', file_url.split('/')[-1])
                file_type = request.data.get('file_type', '').lower()
                
                request.data['file_name'] = file_name
                request.data['file_type'] = file_type

            # Create serializer for the file
            serializer = SharedFileSerializer(data=request.data)

            if serializer.is_valid():
                # Save the file
                file_obj = serializer.save()
                
                # Generate description for images
                image_url = None
                if uploaded_file and file_type in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    image_url = file_obj.get_file_url()
                elif file_url and file_type in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    image_url = file_url
                    
                if image_url:
                    try:
                        # Build full URL for the image if it's a relative path
                        if image_url.startswith('/'):
                            full_url = request.build_absolute_uri(image_url)
                        else:
                            full_url = image_url
                            
                        image_tags = generate_tag(full_url)
                        file_obj.file_description = image_tags
                        file_obj.save()
                    except Exception as e:
                        # Continue without description if generation fails
                        print(f"Error generating image description: {e}")

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
                        # Build full URL for the image
                        file_url = shared_file.get_file_url()
                        if file_url.startswith('/'):
                            full_url = request.build_absolute_uri(file_url)
                        else:
                            full_url = file_url
                            
                        # Generate description for image
                        image_tags = generate_tag(full_url)
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
        
        # Convert relative URLs to absolute URLs
        if query_image_url and query_image_url.startswith('/'):
            query_image_url = request.build_absolute_uri(query_image_url)
        
        # Get all image URLs and convert relative paths to absolute URLs
        image_urls = []
        for img in SharedFile.objects.all():
            img_url = img.get_file_url()
            if img_url and img_url.startswith('/'):
                img_url = request.build_absolute_uri(img_url)
            image_urls.append(img_url)
        
        similar_images = search_similar_images(query_image_url, image_urls)

        return Response(similar_images)
