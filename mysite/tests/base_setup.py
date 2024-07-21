import os

import django


def set_up():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

    django.setup()
