from .base_setup import set_up

set_up()

from django.test import Client, TestCase
from django.urls import reverse

from registration.models import User
from user_profile.models import Image, Like, Post, PostPhoto, Tag, UserProfile


class UrlsTestRegistration(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_page(self):
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        url = reverse('login_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class UrlsTestUserProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com',
            password='12345',
            confirmation_code='fgsdfsd'
        )
        self.user_profile = UserProfile.objects.create(
            bio='testbio',
            first_name='testfirst',
            last_name='testlast'
        )
        self.image = Image.objects.create(
            user_profile=self.user_profile,
            image_url='some_url',
            public_id='some_id'
        )
        self.post = Post.objects.create(
            user_id=self.user_profile,
            content='Test content'
        )

        self.tag1 = Tag.objects.create(name='tag1')
        self.tag2 = Tag.objects.create(name='tag2')

    def test_create_user_page(self):
        self.client.login(
            username='testuser',
            password='12345',
        )

        url = reverse('create_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        self.client.force_login(self.user)

        session = self.client.session
        session['user_id'] = self.user_profile.id
        session.save()

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        image_url = self.image.image_url
        self.assertContains(response, f'<img src="{image_url}"')

    def test_profile_page(self):
        self.client.login(
            username='testuser',
            password='12345'
        )
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_post_page(self):
        self.client.force_login(self.user)

        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        response = self.client.post(reverse('create_post'), {
            'content': self.post.content,
            'tags': [self.tag1.id, self.tag2.id]
        })

        self.assertEqual(response.status_code, 200)

        self.assertTrue(Post.objects.filter(
            user_id=self.user.id,
            content='Test content'
        ).exists())

    def test_tag_page(self):
        self.client.login(
            username='testuser',
            password='12345'
        )
        url = reverse('create_tag')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_post_authenticated(self):
        self.client.force_login(self.user)

        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        response = self.client.post(reverse(
            'delete_post',
            kwargs={'post_id': self.post.id}
        ))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
