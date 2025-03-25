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
            request.data['shared_by'] = request.user.id
            if request.data['file_type'].lower() == "png" or request.data['file_type'].lower() == "jpg" or request.data['file_type'].lower() == "webp" or request.data['file_type'].lower() == "jpeg":
                image_tags = generate_tag(request.data['file'])
            serializer = SharedFileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['file_description'] = image_tags

                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        shared_files = SharedFileSerializer(
            request.user.sharedfile_set.all(), many=True
        )
        return Response(shared_files.data)

    def put(self, request, pk):
        try:
            shared_file = request.user.sharedfile_set.get(pk=pk)
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
