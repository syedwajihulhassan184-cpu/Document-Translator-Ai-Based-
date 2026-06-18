from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import TranslationJobSerializer
from rest_framework.permissions import IsAuthenticated
import fitz
from accounts.utils import check_quota
from .tasks import translate_job
from .models import TranslationJob
from django.shortcuts import get_object_or_404
# Create your views here.

class TranslationJobCreateApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TranslationJobSerializer(data=request.data)
        if serializer.is_valid():
            input_file = serializer.validated_data['input_file']
            doc = fitz.open(input_file.storage_key)
            page_count = doc.page_count
            doc.close()
            allowed, error = check_quota(user=request.user, page_count=page_count)
            if not allowed:
                return Response({'error':error}, status=status.HTTP_400_BAD_REQUEST)
            instance = serializer.save(user=request.user)
            instance.total_pages = page_count
            instance.save()
            translate_job.delay(instance.id)
            request.user.pages_used_this_month += page_count
            request.user.save()
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
