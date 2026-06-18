from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import TranslationJobSerializer
from rest_framework.permissions import IsAuthenticated
import fitz
from .tasks import dummy_translate_job
from .models import TranslationJob
from django.shortcuts import get_object_or_404
# Create your views here.

class TranslationJobCreateApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TranslationJobSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            doc = fitz.open(instance.input_file.storage_key)
            page_count = doc.page_count
            doc.close()
            instance.total_pages = page_count
            instance.save()
            dummy_translate_job.delay(instance.id)
            return Response({'id': instance.id, 'status': instance.status}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TranslationJobDetailApiView(APIView):

    def get(self, request, pk):
        job = get_object_or_404(TranslationJob, pk=pk, user=request.user)
        progress = (job.processed_pages / job.total_pages * 100) if job.total_pages > 0 else 0
        return Response({
            'status': job.status,
            'progress': round(progress, 2),
            'error_message': job.error_message
        }, status=status.HTTP_200_OK)
