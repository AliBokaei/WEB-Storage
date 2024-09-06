import os
import boto3
import logging
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from botocore.exceptions import ClientError
from django.conf import settings

from storage.models import UploadedFile

# Configure logging
logging.basicConfig(level=logging.INFO)

def upload_file_to_s3(file_path, object_name, bucket_name):
    try:
        # Create an S3 resource
        s3_resource = boto3.resource(
            's3',
            endpoint_url='https://s3.ir-thr-at1.arvanstorage.ir/',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    except Exception as exc:
        logging.error(exc)
        return False

    try:
        # Get the bucket
        bucket = s3_resource.Bucket(bucket_name)

        # Open the file in binary read mode
        with open(file_path, "rb") as file:
            # Upload the file
            bucket.put_object(
                ACL='private',
                Body=file,
                Key=object_name
            )
        logging.info(f"File {object_name} uploaded to {bucket_name}.")
        return True
    except ClientError as e:
        logging.error(e)
        return False

@login_required
def upload_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        file_path = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_path)

        object_name = uploaded_file.name  # This should be dynamically set based on the uploaded file
        bucket_name = 'storage-kazem-and-ali'  # Replace with your bucket name

        success = upload_file_to_s3(file_path, object_name, bucket_name)
        if success:
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{object_name}"
            UploadedFile.objects.create(
                file_name=object_name,
                file_link=file_url,
                file_type=uploaded_file.content_type,
                size=uploaded_file.size,
                uploaded_by=request.user
            )
            os.remove(file_path)  # Remove the file from local storage
            logging.info("File uploaded and database entry created successfully")
        else:
            logging.error("File upload failed")

    return redirect('/home/')

