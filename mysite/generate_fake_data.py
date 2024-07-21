import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registration.settings')
django.setup()

from faker import Faker

from registration.models import User
from user_profile.models import Image, UserProfile


def generate_fake_user_profiles(num_profiles: int):
    fake = Faker()
    for _ in range(num_profiles):
        first_name = fake.first_name()
        last_name = fake.last_name()
        bio = fake.text(max_nb_chars=100)
        profile_picture = fake.image_url()
        random_integer = fake.random_int(min=1, max=num_profiles)

        User.objects.create_user(
            email=fake.email(),
            username=fake.user_name(),
            confirmation=True
        )
        user_profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name,
            bio=bio
        )

        Image.objects.create(
            user_profile=user_profile,
            image_url=profile_picture,
            public_id=random_integer
        )


if __name__ == '__main__':
    generate_fake_user_profiles(10)
