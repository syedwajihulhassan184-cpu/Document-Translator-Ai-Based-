from django.urls import path
from .views import FileUploadView


urlpatterns = [
    path('api/file/', FileUploadView.as_view(), name='upload-file'),
]