from django.urls import path
from .views import (
    TranslationJobCreateApiView, TranslationJobDetailApiView, 
    TranslationJobDownloadView
)


urlpatterns = [
    path('api/job/', TranslationJobCreateApiView.as_view(), name='create-job'),
    path('api/jobs/<int:pk>', TranslationJobDetailApiView.as_view(), name='see-job'),
    path('api/jobs/<int:pk>/download/', TranslationJobDownloadView.as_view(), name='download-translated-document')
]