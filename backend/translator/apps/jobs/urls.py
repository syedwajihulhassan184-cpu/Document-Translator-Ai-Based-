from django.urls import path
from .views import TranslationJobCreateApiView, TranslationJobDetailApiView


urlpatterns = [
    path('api/job/', TranslationJobCreateApiView.as_view(), name='create-job'),
    path('api/jobs/<int:pk>', TranslationJobDetailApiView.as_view(), name='see-job')
]