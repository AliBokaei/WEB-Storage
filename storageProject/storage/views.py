import os
import boto3
import logging
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth.models import User
from .forms import SearchForm
from .models import UploadedFile, FileShare
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage

# Configure logging
logging.basicConfig(level=logging.INFO)


# Create your views here.
@login_required
def home(request):
    current_user = request.user
    files = UploadedFile.objects.filter(uploaded_by=current_user).order_by('-upload_date')
    # files = UploadedFile.objects.filter(uploaded_by=current_user)

    shared_files = UploadedFile.objects.filter(shared_with=current_user)
    print(shared_files)

    totalSize = 0
    for file in files:
        totalSize += file.size

    for shared_file in shared_files:
        totalSize += shared_file.size

    print(totalSize)

    # users = User.objects.all()
    users = User.objects.exclude(id=current_user.id)

    # pagination
    for shared_file in shared_files:
        shared_file.type = 'shared'
    for file in files:
        file.type = 'owned'

    # all_posts = list(files) + list(shared_files)
    # all_posts.order_by('-upload_date')

    all_posts_not_sorted = list(files) + list(shared_files)
    all_posts = sorted(all_posts_not_sorted, key=lambda post: post.upload_date, reverse=True)

    paginator = Paginator(all_posts, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_info': request.session.get('user_info', {}),
        # 'files': files,
        'users': users,
        'total_size': totalSize,
        # 'shared_files': shared_files,
        'page_obj': page_obj

    }
    return render(request, 'indexHome.htm', context)


@login_required
def download_file_from_s3(bucket_name, object_name, download_path, version_id=None):
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

        extra_args = {'VersionId': version_id} if version_id else {}

        # Download the file
        bucket.download_file(
            object_name,
            download_path,
            ExtraArgs=extra_args
        )
        logging.info(f"File {object_name} downloaded from {bucket_name}.")
        return True
    except ClientError as e:
        logging.error(e)
        return False


# @login_required
# def download_view(request, file_id):
#     try:
#         uploaded_file = UploadedFile.objects.get(id=file_id)
#     except UploadedFile.DoesNotExist:
#         raise Http404("File does not exist")
#
#     file_name = uploaded_file.file_name
#     bucket_name = settings.AWS_STORAGE_BUCKET_NAME
#     download_path = uploaded_file.file_link
#
#     success = download_file_from_s3(bucket_name, file_name, download_path)
#     if success:
#         with open(download_path, 'rb') as file:
#             response = HttpResponse(file.read(), content_type='application/octet-stream')
#             response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#             os.remove(download_path)  # Clean up the temporary file
#             return response
#     else:
#         return HttpResponse("Failed to download the file", status=500)

@login_required
def download_view(request, file_id):
    BUCKET_NAME = 'storage-kazem-and-ali'
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    # uploaded_file = get_object_or_404(UploadedFile, id=file_id, uploaded_by=request.user)
    object_name = uploaded_file.file_name

    try:
        s3_resource = boto3.resource(
            's3',
            endpoint_url='https://s3.ir-thr-at1.arvanstorage.ir/',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    except Exception as exc:
        logging.error(exc)
        return HttpResponse("Error initializing S3 resource", status=500)

    try:
        download_path = os.path.join('download', object_name)

        s3_resource.Bucket(BUCKET_NAME).download_file(object_name, download_path)
        logging.info(f"File {object_name} downloaded successfully to {download_path}.")

        with open(download_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename={object_name}'
            return response

    except ClientError as e:
        logging.error(e)
        return HttpResponse("Error downloading file", status=500)


@login_required
def delete_view(request, file_id):
    BUCKET_NAME = 'storage-kazem-and-ali'
    delete_file = get_object_or_404(UploadedFile, id=file_id)
    object_name = delete_file.file_name

    try:
        s3_resource = boto3.resource(
            's3',
            endpoint_url='https://s3.ir-thr-at1.arvanstorage.ir/',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    except Exception as exc:
        logging.error(exc)
    else:
        try:
            bucket_name = BUCKET_NAME
            object_name = object_name
            bucket = s3_resource.Bucket(bucket_name)
            object = bucket.Object(object_name)
            response = object.delete()
            logging.info(f"Object {object_name} deleted successfully from bucket {bucket_name}.")
        except ClientError as e:
            logging.error(e)

    delete_file.delete()
    logging.info(f"Record for {delete_file.file_name} deleted successfully from database.")

    return redirect('/home/')


def search_view(request):
    print("serach")
    form = SearchForm()
    query = None
    totalSize = 0
    page_obj = None
    results = []
    if request.method == 'POST':
        form = SearchForm(request.POST)  # correct
        current_user = request.user
        if form.is_valid():
            query = form.cleaned_data['query']
            print("Search query:", query)

            files = UploadedFile.objects.filter(
                uploaded_by=current_user,
                file_name__icontains=query
            ).distinct()

            shared_files = UploadedFile.objects.filter(
                shared_with=current_user,
                file_name__icontains=query
            ).distinct()

            for file in files:
                totalSize += file.size

            for shared_file in shared_files:
                totalSize += shared_file.size

            for shared_file in shared_files:
                shared_file.type = 'shared'
            for file in files:
                file.type = 'owned'

            all_posts_not_sorted = list(files) + list(shared_files)
            all_posts = sorted(all_posts_not_sorted, key=lambda post: post.upload_date, reverse=True)

            paginator = Paginator(all_posts, 24)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        else:
            return redirect('/home/')

    print("Search results:", results)

    context = {
        'files': results,
        'user_info': request.session.get('user_info', {}),
        'total_size': totalSize,
        'page_obj': page_obj,

    }

    return render(request, 'indexHome.htm', context)


@csrf_protect
def save_selected_users(request):
    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users')
        file_id = request.POST.get('file_id')
        print("file:")
        print(file_id)

        print("selected_users:")
        print(selected_users)

        file = UploadedFile.objects.get(id=file_id)
        # file.shared_with.clear()

        shared_users = file.shared_with.values_list('id', flat=True)
        selected_users_new = [user_id for user_id in selected_users if int(user_id) not in shared_users]

        for user_id in selected_users_new:
            user = User.objects.get(id=user_id)
            # file.shared_with.add(user)
            print(f"File {file.file_name} shared with user {user_id}.")
            share_email(request, user, file)

        file.shared_with.clear()
        for user_id in selected_users:
            user = User.objects.get(id=user_id)
            file.shared_with.add(user)
            print(f"File {file.file_name} added with user {user_id}.")

        return redirect('/home/')

    return redirect('/home/')


def share_email(request, user, file):
    mail_subject = f'Access to object {file.file_name}'
    message = render_to_string("share_acc.html", {
        'user': user.username,
        'file': file.file_name
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    try:
        email.send(fail_silently=False)
        print(f"Sending email access to object {file.file_name} "
              f"with user {user.username} was successfully.")

        return redirect('/home/')
    except Exception as e:
        print(f"Error sending email access to object {file.file_name} "
              f"with user: {user.username}.")
        return redirect('/home/')
