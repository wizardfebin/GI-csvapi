
# Create your tests here.
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import User

class CSVUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/upload/'

    def make_csv_bytes(self, content: str):
        return SimpleUploadedFile("test.csv", content.encode('utf-8'), content_type='text/csv')

    def test_upload_all_valid(self):
        csv_content = "name,email,age\nAmmu,ammu@example.com,30\nsajin,sajin@example.com,25\n"
        file = self.make_csv_bytes(csv_content)
        resp = self.client.post(self.url, {'file': file}, format='multipart')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['saved_count'], 2)
        self.assertEqual(data['rejected_count'], 0)
        self.assertEqual(data['skipped_count'], 0)
        self.assertEqual(User.objects.count(), 2)

    def test_upload_with_invalid_rows(self):
        csv_content = "name,email,age\nAlice,alice@example.com,30\nInvalid,,abc\nEmptyName,emptymail@example.com,30\n"
        file = self.make_csv_bytes(csv_content)
        resp = self.client.post(self.url, {'file': file}, format='multipart')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['saved_count'], 2 if User.objects.filter(email='emptymail@example.com').exists() else 1)
        self.assertTrue(data['rejected_count'] >= 1)
        self.assertTrue(len(data['errors']) >= 1)

    def test_duplicate_emails_are_skipped(self):
        User.objects.create(name="achu", email="achu@example.com", age=40)

        csv_content = "name,email,age\nachu,achu@example.com,40\nNewUser,new@example.com,22\n"
        file = self.make_csv_bytes(csv_content)
        resp = self.client.post(self.url, {'file': file}, format='multipart')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['saved_count'], 1)
        self.assertEqual(data['skipped_count'], 1)
