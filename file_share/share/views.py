from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserProfileSerializer, SharedFileSerializer
from .models import SharedFile, TrashLog, StarredFile
from .desc_generator import generate_tag
from .similar_img import search_similar_images
# added while creating template views:
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, Http404, FileResponse
import os
from django.conf import settings
from django.conf import settings
from django.db import models
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
                    # Use the file path directly instead of URL
                    file_path = str(shared_file.file)  # This gives us the relative path like 'uploads/filename.jpg'
                    
                    image_tags = generate_tag(file_path)
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
    # Get file type filter and search query from query params
    file_type = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '').strip()
    
    # Get all files for the current user
    shared_files = request.user.sharedfile_set.all()
    
    # Apply search filter if provided
    if search_query:
        # Search in file names, descriptions, and file types using case-insensitive contains
        shared_files = shared_files.filter(
            models.Q(file_name__icontains=search_query)
        )
    
    # Apply file type filter if specified
    if file_type != 'all':
        if file_type == 'images':
            shared_files = shared_files.filter(file_type__in=['png', 'jpg', 'jpeg', 'webp', 'gif'])
        elif file_type == 'videos':
            shared_files = shared_files.filter(file_type__in=['mp4', 'webm', 'mov', 'avi'])
        elif file_type == 'documents':
            # Exclude images and videos
            shared_files = shared_files.exclude(file_type__in=['png', 'jpg', 'jpeg', 'webp', 'gif', 'mp4', 'webm', 'mov', 'avi'])
    
    # Order by most recent first
    shared_files = shared_files.order_by('-share_time')
    
    # Add starred status to each file
    for file in shared_files:
        file.is_starred = file.is_starred_by(request.user)
    
    context = {
        'shared_files': shared_files,
        'current_search': search_query,
        'current_type': file_type
    }
    
    return render(request, 'share/dashboard.html', context)

@login_required
def image_search_view(request):
    return render(request, 'share/image-search.html')

@login_required
def starred_view(request):
    """View for showing only starred files"""
    # Get all starred files for the current user
    starred_files = StarredFile.objects.filter(user=request.user).select_related('file')
    
    # Extract the actual SharedFile objects and mark them as starred
    shared_files = []
    for starred in starred_files:
        file = starred.file
        file.is_starred = True  # All files in this view are starred
        shared_files.append(file)
    
    context = {
        'shared_files': shared_files,
        'page_title': 'Starred Files'
    }
    
    return render(request, 'share/starred.html', context)

@login_required
def trash_view(request):
    """View for showing deleted files log"""
    # Get all trash logs for the current user
    trash_logs = TrashLog.objects.filter(deleted_by=request.user)
    
    context = {
        'trash_logs': trash_logs,
        'page_title': 'Trash'
    }
    
    return render(request, 'share/trash.html', context)

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
                        # Use the file path directly instead of URL
                        file_path = str(file_obj.file)  # This gives us the relative path like 'uploads/filename.jpg'
                            
                        image_tags = generate_tag(file_path)
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
                        # Use the file path directly instead of URL
                        file_path = str(shared_file.file)  # This gives us the relative path like 'uploads/filename.jpg'
                            
                        # Generate description for image
                        image_tags = generate_tag(file_path)
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
            
            # Create trash log before deleting
            TrashLog.objects.create(
                file_name=shared_file.file_name,
                file_size=shared_file.file_size,
                file_type=shared_file.file_type,
                original_share_type=shared_file.share_type,
                original_share_time=shared_file.share_time,
                file_description=shared_file.file_description,
                original_file_id=shared_file.id,
                deleted_by=request.user
            )
            
            # Remove any star records for this file
            StarredFile.objects.filter(file=shared_file).delete()
            
            # Now delete the actual file
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
        
        if not query_image_url:
            return Response({'error': 'No image URL provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert URL to file path
        if query_image_url.startswith('/media/uploads/'):
            query_image_filename = query_image_url.replace('/media/uploads/', '')
            query_image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', query_image_filename)
        elif query_image_url.startswith('/protected-media/uploads/'):
            query_image_filename = query_image_url.replace('/protected-media/uploads/', '')
            query_image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', query_image_filename)
        else:
            return Response({'error': 'Invalid image URL format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if query image file exists
        if not os.path.exists(query_image_path):
            return Response({'error': 'Query image file not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all image file paths
        image_paths = []
        image_files = []
        for shared_file in SharedFile.objects.filter(file_type__in=['png', 'jpg', 'jpeg', 'webp', 'gif']):
            if shared_file.file:
                file_path = shared_file.file.path
                if os.path.exists(file_path):
                    image_paths.append(file_path)
                    image_files.append(shared_file)
        
        try:
            similar_images = search_similar_images(query_image_path, image_paths)
            
            # Convert file paths back to file info for response
            result = []
            for file_path, similarity in similar_images:
                # Find the corresponding SharedFile object
                for shared_file in image_files:
                    if shared_file.file.path == file_path:
                        result.append({
                            'id': shared_file.id,
                            'file_name': shared_file.file_name,
                            'file_url': shared_file.get_file_url(),
                            'similarity': similarity,
                            'file_size': shared_file.file_size,
                            'share_time': shared_file.share_time.isoformat(),
                        })
                        break
            
            return Response(result)
            
        except Exception as e:
            return Response({'error': f'Error processing images: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StarredFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        """Star a file"""
        try:
            shared_file = SharedFile.objects.get(id=file_id, shared_by=request.user)
            
            # Check if already starred
            starred_file, created = StarredFile.objects.get_or_create(
                user=request.user,
                file=shared_file
            )
            
            if created:
                return Response({'message': 'File starred successfully', 'starred': True})
            else:
                return Response({'message': 'File already starred', 'starred': True})
                
        except SharedFile.DoesNotExist:
            return Response({'error': 'File not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, file_id):
        """Unstar a file"""
        try:
            shared_file = SharedFile.objects.get(id=file_id, shared_by=request.user)
            
            try:
                starred_file = StarredFile.objects.get(user=request.user, file=shared_file)
                starred_file.delete()
                return Response({'message': 'File unstarred successfully', 'starred': False})
            except StarredFile.DoesNotExist:
                return Response({'message': 'File was not starred', 'starred': False})
                
        except SharedFile.DoesNotExist:
            return Response({'error': 'File not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
