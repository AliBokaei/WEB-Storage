from django.test import TestCase
from django.contrib.auth.models import User
from .models import UploadedFile
from datetime import datetime
from django.test import TestCase
from .forms import SearchForm
from django.test import TestCase
from django.contrib.admin.sites import site
from .admin import UploadedFileAdmin, FileShareAdmin
from .models import UploadedFile, FileShare


class UploadedFileAdminTest(TestCase):
    def setUp(self):
        self.admin = UploadedFileAdmin(UploadedFile, site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ('file_name', 'file_link', 'file_type', 'size', 'upload_date', 'uploaded_by')
        )

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ('file_name', 'uploaded_by__username')
        )

    def test_list_filter(self):
        self.assertEqual(
            self.admin.list_filter,
            ('upload_date', 'file_type', 'uploaded_by')
        )


class FileShareAdminTest(TestCase):
    def setUp(self):
        self.admin = FileShareAdmin(FileShare, site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ('file', 'user', 'shared_at')
        )

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ('file__title', 'user__username')
        )


class SearchFormTest(TestCase):
    def test_valid_form_data(self):
        form_data = {'query': 'test search'}
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_form_data(self):
        form_data = {'query': ''}
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['query'], ['This field is required.'])

    def test_long_query(self):
        form_data = {'query': 'a' * 101}  # 101 کاراکتر، بیشتر از max_length
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['query'], ['Ensure this value has at most 100 characters (it has 101).'])

class UploadedFileModelTest(TestCase):
    def setUp(self):
        # ایجاد کاربر تستی
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.user3 = User.objects.create_user(username='testuser3', password='password')

        # ایجاد یک فایل آپلود شده تستی
        self.uploaded_file = UploadedFile.objects.create(
            file_name='testfile.txt',
            file_link='http://example.com/testfile.txt',
            file_type='text',
            size=1024,
            uploaded_by=self.user1
        )
        self.uploaded_file.shared_with.set([self.user2, self.user3])

    def test_file_creation(self):
        self.assertEqual(self.uploaded_file.file_name, 'testfile.txt')
        self.assertEqual(self.uploaded_file.file_link, 'http://example.com/testfile.txt')
        self.assertEqual(self.uploaded_file.file_type, 'text')
        self.assertEqual(self.uploaded_file.size, 1024)
        self.assertEqual(self.uploaded_file.uploaded_by, self.user1)
        self.assertIn(self.user2, self.uploaded_file.shared_with.all())
        self.assertIn(self.user3, self.uploaded_file.shared_with.all())

    def test_file_str_method(self):
        expected_str = "testfile.txt uploaded by testuser1"
        self.assertEqual(str(self.uploaded_file), expected_str)

    def test_update_file_name(self):
        self.uploaded_file.file_name = 'newname.txt'
        self.uploaded_file.save()
        self.assertEqual(self.uploaded_file.file_name, 'newname.txt')

    def test_delete_file(self):
        file_id = self.uploaded_file.id
        self.uploaded_file.delete()
        self.assertFalse(UploadedFile.objects.filter(id=file_id).exists())

    def test_shared_with_users(self):
        shared_users = self.uploaded_file.shared_with.all()
        self.assertIn(self.user2, shared_users)
        self.assertIn(self.user3, shared_users)
