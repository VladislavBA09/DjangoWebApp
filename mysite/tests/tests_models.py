from .base_setup import set_up

set_up()


from django.test import TestCase

from registration.models import User
from user_profile.models import (Dislike, Follow, Image, Like, Post, PostPhoto,
                                 Tag, UserProfile)


class RegistrationTestCase(TestCase):
    def setUp(self):
        User.objects.create(
            email="test",
            password='test',
            confirmation_code='123',
            confirmation=False,
            username='username'
        )

    def test_create_new_user(self):
        new_user = User.objects.get(email="test")

        self.assertEqual(new_user.email, 'test')
        self.assertEqual(new_user.password, 'test')
        self.assertEqual(new_user.confirmation_code, '123')
        self.assertEqual(new_user.confirmation, False)
        self.assertEqual(new_user.username, 'username')


class UserProfileTestCase(TestCase):
    def setUp(self):
        UserProfile.objects.create(
            bio="aboutme",
            first_name='name',
            last_name='lastname',
        )
        UserProfile.objects.create(
            bio="1234",
            first_name='test',
            last_name='test',
        )
        new_profile = UserProfile.objects.get(first_name='name').id

        Image.objects.create(
            user_profile_id=new_profile,
            image_url='some_url',
            public_id='some_id'
        )
        post = Post.objects.create(
            user_id_id=new_profile,
            content='content',
        )

        PostPhoto.objects.create(
            post_id=post.id,
            image_url='some_url',
            public_id='some_id'
        )

        PostPhoto.objects.create(
            post_id=post.id,
            image_url='some_url',
            public_id='some_id'
        )

    def test_create_new_profile(self):
        new_profile = UserProfile.objects.get(first_name='name')

        self.assertEqual(new_profile.last_name, 'lastname')
        self.assertEqual(new_profile.bio, 'aboutme')

    def test_create_image(self):
        new_profile = UserProfile.objects.get(first_name='name').id
        new_image = Image.objects.get(user_profile_id=new_profile)

        self.assertEqual(new_image.image_url, 'some_url')

    def test_create_tag(self):
        Tag.objects.create(
            name='newtag'
        )
        new_tag = Tag.objects.get(id=1)

        self.assertEqual(new_tag.name, 'newtag')

    def test_create_user_post(self):
        post = Post.objects.get(user_id__first_name='name')

        post_photos = PostPhoto.objects.filter(post=post)

        self.assertEqual(post_photos.count(), 2)

    def test_like_post(self):
        new_profile = UserProfile.objects.get(first_name='name').id
        new_post = Post.objects.get(content='content').id
        Like.objects.create(
            user_id=new_profile,
            post_id=new_post
        )
        new_like = Like.objects.get(user_id=1)
        self.assertEqual(new_like.post_id, 1)

    def test_dislike_post(self):
        new_profile = UserProfile.objects.get(first_name='name').id
        new_post = Post.objects.get(content='content').id
        Like.objects.create(
            user_id=new_profile,
            post_id=new_post
        )
        new_dislike = Like.objects.get(user_id=1)
        self.assertEqual(new_dislike.post_id, 1)

    def test_create_following(self):
        first_profile = UserProfile.objects.get(first_name='name').id
        second_profile = UserProfile.objects.get(first_name='test').id
        Follow.objects.create(
            follower_id=first_profile,
            following_id=second_profile
        )
        new_follow = Follow.objects.get(id=first_profile)
        self.assertEqual(new_follow.following_id, 2)
