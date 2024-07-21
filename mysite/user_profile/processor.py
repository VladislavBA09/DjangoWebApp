import os
from pathlib import Path

import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
import environ
from django.shortcuts import render
from django.contrib.auth import logout


from .models import Image, Post, PostPhoto, UserProfile

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env_cloudinary'))


cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)


def upload_image_to_cloudinary_from_neighboring_folder(
        image_filename,
        user_profile: UserProfile
) -> Image:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_file_path = os.path.join(project_root, image_filename)
    upload_result = upload(image_file_path)
    image_url = upload_result["secure_url"]
    public_id = upload_result['public_id']
    image = Image.objects.create(
        user_profile=user_profile,
        image_url=image_url,
        public_id=public_id
    )

    return image


def upload_image_to_cloudinary(image_file, user_profile: UserProfile) -> Image:
    upload_result = cloudinary.uploader.upload(image_file)
    image_url = upload_result["secure_url"]
    public_id = upload_result['public_id']
    image = Image.objects.create(
        user_profile=user_profile,
        image_url=image_url,
        public_id=public_id
    )
    return image


def upload_post_photo_to_cloudinary(image_list: list, post: Post):
    for elements in image_list:
        upload_result = cloudinary.uploader.upload(elements)
        image_url = upload_result["secure_url"]
        public_id = upload_result['public_id']
        PostPhoto.objects.create(
            post=post,
            image_url=image_url,
            public_id=public_id
        )


def delete_image_from_cloudinary(user_id: int):
    image = Image.objects.get(user_profile_id=user_id)
    cloudinary.uploader.destroy(image.public_id)
    image.delete()


def delete_post_photo_from_cloudinary(post_id: int):
    photos = PostPhoto.objects.filter(post_id=post_id)
    for photo in photos:
        cloudinary.uploader.destroy(photo.public_id)


def logout_view(request):
    logout(request)
    request.session.flush()
    return render(
        request,
        'login_user.html'
    )
