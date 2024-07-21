from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from registration.models import User

from .forms import PostForm
from .models import (Dislike, Follow, Image, Like, Post, PostPhoto, Tag,
                     UserProfile)
from .processor import (delete_image_from_cloudinary,
                        delete_post_photo_from_cloudinary,
                        upload_image_to_cloudinary,
                        upload_post_photo_to_cloudinary,
                        upload_image_to_cloudinary_from_neighboring_folder)


class HomeView(View, LoginRequiredMixin):
    def get(self, request):
        user_id = request.user.id

        my_image = Image.objects.filter(user_profile_id=user_id).first()

        my_data = UserProfile.objects.get(id=user_id)

        if not my_data:
            return redirect(reverse('login_user'))

        followers = Follow.objects.filter(
            following_id=user_id
        ).values_list('follower_id', flat=True)

        follower_profiles = UserProfile.objects.filter(id__in=followers)

        follower_images = {}
        for follower in follower_profiles:
            follower_images[follower] = Image.objects.filter(
                user_profile_id=follower.id
            )

        posts = Post.objects.filter(user_id_id=user_id)
        post_photos = {}

        for post in posts:
            post.show_alternate_photo = False
            first_photo = post.postphoto_set.first()
            if first_photo:
                post.photo_url = first_photo.image_url
                post_photos[post] = PostPhoto.objects.filter(post=post)

        liked_posts = set(Like.objects.filter(
            user_id=user_id
        ).values_list('post_id', flat=True))

        disliked_posts = set(Dislike.objects.filter(
            user_id=user_id
        ).values_list('post_id', flat=True))

        context = {
            'my_image': my_image,
            'my_data': my_data,
            'follower_images': follower_images,
            'posts': posts,
            'post_photos': post_photos,
            'liked_posts': liked_posts,
            'disliked_posts': disliked_posts
        }
        return render(request, 'my_profile.html', context)


class LikeView(LoginRequiredMixin, View):
    def get(self, request):
        next_url = request.GET.get('next', reverse('home'))
        return redirect(next_url)

    def post(self, request, post_id: int):
        user_id = request.user.id
        like, created = Like.objects.get_or_create(
            user_id=user_id,
            post_id=post_id
        )
        if not created:
            like.delete()

        next_url = request.POST.get('next', reverse('home'))
        return redirect(next_url)


class DislikeView(View, LoginRequiredMixin):
    def get(self, request):
        next_url = request.GET.get('next', reverse('home'))
        return redirect(next_url)

    def post(self, request, post_id: int):
        user_id = request.user.id
        dislike, created = Dislike.objects.get_or_create(
            user_id=user_id,
            post_id=post_id
        )
        if not created:
            dislike.delete()

        next_url = request.POST.get('next', reverse('home'))
        return redirect(next_url)


class DelPostView(View, LoginRequiredMixin):
    def get(self):
        return redirect('home')

    def post(self, request, post_id: int):
        user_id = request.user.id
        post = get_object_or_404(Post, id=post_id)
        if post.user_id_id == user_id:
            delete_post_photo_from_cloudinary(post_id)
            post.delete()
        return redirect('home')


class CreateProfileView(View, LoginRequiredMixin):
    def get(self, request):
        user_id = request.user.id

        user = User.objects.get(id=user_id)

        if not user.confirmation:
            user_profile, created = UserProfile.objects.get_or_create(
                id=user_id,
                defaults={
                    'first_name': user.first_name or 'None',
                    'last_name': user.last_name or 'None',
                    'bio': 'None'
                }
            )
            user.confirmation = True
            user.save()
            upload_image_to_cloudinary_from_neighboring_folder('None.png', user_profile)
            return redirect('home')
        user_profile_exists = UserProfile.objects.filter(id=user_id).exists()
        if user_profile_exists:
            return redirect('home')

        return render(request, 'create_profile.html')

    def post(self, request):
        user_id = request.user.id
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')

        if not all([first_name, last_name, bio, profile_picture]):
            return render(
                request,
                'create_profile.html',
                {'error': "Please upload an data before saving."}
            )

        user_profile, created = UserProfile.objects.get_or_create(
            id=user_id
        )
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.bio = bio
        user_profile.save()


        try:
            upload_image_to_cloudinary(profile_picture, user_profile)
        except ValueError as e:
            return render(
                request,
                'create_profile.html',
                {'error': str(e)}
            )

        return redirect('home')


class EditProfView(View, LoginRequiredMixin):
    def get(self, request):
        return render(
            request,
            'edit_profile.html',
            {'error': 'Invalid request method'}
        )

    def post(self, request):
        user_id = request.user.id
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')

        user_profile, created = UserProfile.objects.get_or_create(
            id=user_id
        )

        if first_name:
            user_profile.first_name = first_name
        if last_name:
            user_profile.last_name = last_name
        if bio:
            user_profile.bio = bio

        if profile_picture:
            delete_image_from_cloudinary(user_id)

            upload_image_to_cloudinary(profile_picture, user_profile)

        user_profile.save()

        return render(
            request,
            'edit_profile.html',
            {'success': 'Data has been changed'}
        )


class PostView(View, LoginRequiredMixin):
    def get(self, request):
        form = PostForm()
        tags = Tag.objects.all()
        return render(
            request,
            'create_post.html',
            {'form': form, 'tags': tags}
        )

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            user_id = request.user.id
            content = form.cleaned_data['content']
            tag_ids = form.cleaned_data['tags']
            post_pictures = form.files.getlist('post_pictures')

            user_profile = UserProfile.objects.get(id=user_id)
            post = Post.objects.create(
                user_id=user_profile,
                content=content
            )
            upload_post_photo_to_cloudinary(post_pictures, post)

            for tag_id in tag_ids:
                tag = Tag.objects.get(id=tag_id.id)
                post.tags.add(tag)

            form = PostForm()
            return render(
                request,
                'create_post.html',
                {
                    'form': form,
                    'tags': Tag.objects.all(),
                    'success': 'Post was created'
                }
            )
        else:
            return render(
                request,
                'create_post.html',
                {'form': form, 'tags': Tag.objects.all()}
            )


class TagView(View, LoginRequiredMixin):
    def get(self, request):
        return render(request, 'create_tag.html')

    def post(self, request):
        name = request.POST.get('name')
        hashtag = '#'
        if not name:
            return render(
                request,
                'create_tag.html',
                {'error': 'This field cannot be empty '}
            )

        if Tag.objects.filter(name=hashtag + name).exists():
            return render(
                request,
                'create_tag.html',
                {'error': 'You already have a tag with this name.'}
            )

        new_tag = Tag.objects.create(name=hashtag + name)
        new_tag.save()

        return render(
            request,
            'create_tag.html',
            {'success': 'Tag was created successfully.'}
        )


class SubscriptionView(View, LoginRequiredMixin):
    def get(self, request):
        user_id = request.user.id
        other_users = UserProfile.objects.exclude(id=user_id)
        images = Image.objects.all()

        following_profiles = Follow.objects.filter(
            follower_id=user_id
        ).values_list(
            'following_id',
            flat=True
        )

        subscribed_users = {
            profile: (
                    profile.id in following_profiles
            ) for profile in other_users
        }

        context = {
            'subscribed_users': subscribed_users,
            'users': other_users,
            'images': images,
        }

        return render(request, 'subscription.html', context)


class SubscribeView(LoginRequiredMixin, View):
    def get(self):
        return redirect('subscription')

    def post(self, request):
        user_to_follow_id = request.POST.get('user_to_follow')
        user_to_follow = UserProfile.objects.get(id=user_to_follow_id)

        current_user_id = request.user.id

        Follow.objects.create(
            follower_id=current_user_id,
            following=user_to_follow
        )
        return redirect('subscription')


class UnsubscribeView(View, LoginRequiredMixin):
    def get(self):
        return redirect('subscription')

    def post(self, request):
        user_to_unfollow_id = request.POST.get('user_to_unfollow')
        user_to_follow = UserProfile.objects.get(
            id=user_to_unfollow_id
        )

        current_user_id = request.user.id

        Follow.objects.filter(
            follower_id=current_user_id,
            following_id=user_to_follow
        ).delete()
        return redirect('subscription')


class GuestView(View):
    def get(self, request, user_id: int):
        my_image = Image.objects.filter(user_profile_id=user_id).first()
        my_data = UserProfile.objects.get(id=user_id)

        followers = Follow.objects.filter(
            following_id=user_id
        ).values_list('follower_id', flat=True)
        follower_profiles = UserProfile.objects.filter(id__in=followers)

        follower_images = {}
        for follower in follower_profiles:
            follower_images[follower] = Image.objects.filter(
                user_profile_id=follower.id
            )

        posts = Post.objects.filter(user_id=user_id)

        liked_posts = set(
            Like.objects.filter(
                user_id=request.user.id,
                post_id__in=posts
            ).values_list('post_id', flat=True)
        )
        disliked_posts = set(
            Dislike.objects.filter(
                user_id=request.user.id,
                post_id__in=posts
            ).values_list('post_id', flat=True)
        )

        context = {
            'user_id': user_id,
            'my_image': my_image,
            'my_data': my_data,
            'follower_images': follower_images,
            'posts': posts,
            'liked_posts': liked_posts,
            'disliked_posts': disliked_posts,
        }

        return render(request, 'guest_profile.html', context)


class GuestLikeView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        post_id = request.POST.get('post_id')

        like, created = Like.objects.get_or_create(
            user_id=request.user.id,
            post_id=post_id
        )
        if not created:
            like.delete()

        return redirect(
            reverse(
                'user_profile',
                kwargs={'user_id': user_id}
            )
        )


class GuestDisLikeView(View, LoginRequiredMixin):
    def post(self, request, user_id):
        post_id = request.POST.get('post_id')

        dislike, created = Dislike.objects.get_or_create(
            user_id=request.user.id,
            post_id=post_id
        )
        if not created:
            dislike.delete()

        return redirect(
            reverse(
                'user_profile',
                kwargs={'user_id': user_id}
            )
        )


class DelProfView(View):
    def post(self, request):
        user_id = request.user.id
        if user_id is not None:
            delete_image_from_cloudinary(user_id)

            UserProfile.objects.filter(id=user_id).delete()

            User.objects.filter(id=user_id).delete()

            return redirect(reverse('login_user'))
        return redirect(reverse('login_user'))


class Posts(View):
    def get(self, request):
        user_id = request.user.id

        your_posts = Post.objects.filter(user_id=user_id)

        following_users_ids = Follow.objects.filter(
            follower_id=user_id
        ).values_list('following_id', flat=True)

        following_posts = Post.objects.filter(user_id__in=following_users_ids)

        posts = your_posts | following_posts

        post_photos = {}

        for post in posts:
            post.show_alternate_photo = False
            first_photo = post.postphoto_set.first()
            if first_photo:
                post.photo_url = first_photo.image_url
                post_photos[post] = PostPhoto.objects.filter(post=post)

        liked_posts = set(Like.objects.filter(
            user_id=user_id
        ).values_list('post_id', flat=True))

        disliked_posts = set(Dislike.objects.filter(
            user_id=user_id
        ).values_list('post_id', flat=True))

        context = {
            'posts': posts,
            'post_photos': post_photos,
            'liked_posts': liked_posts,
            'disliked_posts': disliked_posts
        }

        return render(request, 'posts.html', context)
