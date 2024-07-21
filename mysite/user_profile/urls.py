from django.urls import path

from .views import (CreateProfileView, DelPostView, DelProfView, DislikeView,
                    EditProfView, GuestDisLikeView, GuestLikeView, GuestView,
                    HomeView, LikeView, Posts, PostView, SubscribeView,
                    SubscriptionView, TagView, UnsubscribeView)
from .processor import logout_view

urlpatterns = [
    path(
        'create_profile/',
        CreateProfileView.as_view(),
        name='create_profile'
    ),
    path('logout/', logout_view, name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('profile/', EditProfView.as_view(), name='profile'),
    path('create_post/', PostView.as_view(), name='create_post'),
    path('create_tag/', TagView.as_view(), name='create_tag'),
    path(
        'subscription/',
        SubscriptionView.as_view(),
        name='subscription'
    ),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path(
        'like_post/<int:post_id>/',
        LikeView.as_view(),
        name='like_post'
    ),
    path(
        'dislike_post/<int:post_id>/',
        DislikeView.as_view(),
        name='dislike_post'
    ),
    path(
        'delete_post/<int:post_id>/',
        DelPostView.as_view(),
        name='delete_post'
    ),
    path(
        'user_profile/profile/<int:user_id>/',
        GuestView.as_view(),
        name='user_profile'
    ),
    path('delete_profile/', DelProfView.as_view(), name='delete_profile'),
    path(
        'user_profile/guest_like/<int:user_id>/',
        GuestLikeView.as_view(),
        name='guest_like'
    ),
    path(
        'user_profile/guest_dislike/<int:user_id>/',
        GuestDisLikeView.as_view(),
        name='guest_dislike'
    ),
    path('posts', Posts.as_view(), name='posts'),
]
