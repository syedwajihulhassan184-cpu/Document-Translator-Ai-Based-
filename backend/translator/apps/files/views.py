import hashlib
import os
from .models import File
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import FileSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]


    def post(self, request):
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            if file.size > 50 * 1024 * 1024:
                return Response({'error':'File is too large'}, status=status.HTTP_400_BAD_REQUEST)
            checksum = hashlib.sha256(file.read()).hexdigest()
            file.seek(0)
            tmp_path = f'/tmp/{file.name}'
            with open(tmp_path, 'wb') as f:
                f.write(file.read())

            file_instance = File.objects.create(
                user=request.user,
                original_filename=file.name,
                storage_key=tmp_path,
                mime_type=file.content_type,
                size_bytes=file.size,
                checksum_sha256=checksum,
                file_format=serializer.validated_data['file_format'],
            )
            return Response({
                'id':file_instance.id,
                'original_filename':file_instance.original_filename
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
