from django.db import models


class UserProfile(models.Model):
    objects = None
    bio = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, default=False)
    last_name = models.CharField(max_length=50, default=False)

    def __str__(self):
        return self.user.username


class Image(models.Model):
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    image_url = models.CharField(max_length=255, default=False)
    public_id = models.CharField(max_length=255, default=False)

    def __str__(self):
        return self.image_url


class Post(models.Model):
    objects = None
    user_id = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        default=False
    )
    content = models.CharField(max_length=100, default=False)
    tags = models.ManyToManyField('Tag', blank=True)


class PostPhoto(models.Model):
    objects = None
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )
    image_url = models.CharField(max_length=255, default=False)
    public_id = models.CharField(max_length=255, default=False)


class Tag(models.Model):
    objects = None
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Follow(models.Model):
    objects = None
    follower = models.ForeignKey(
        UserProfile,
        related_name='following',
        on_delete=models.CASCADE,
        default=False
    )
    following = models.ForeignKey(
        UserProfile,
        related_name='followers',
        on_delete=models.CASCADE,
        default=False
    )


class Like(models.Model):
    objects = None
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Dislike(models.Model):
    objects = None
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
