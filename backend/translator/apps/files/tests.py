from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import CustomUser
# Create your tests here.

class FileUploadTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_upload_pdf(self):
        fake_pdf = SimpleUploadedFile(
        "test.pdf", b"%PDF-1.4 fake content", content_type='application/pdf'
            )
        response = self.client.post('/api/file/', {
            'file': fake_pdf,
            'file_format': 'pdf'
        }, format='multipart')
        print(response.status_code)
        print(response.data)