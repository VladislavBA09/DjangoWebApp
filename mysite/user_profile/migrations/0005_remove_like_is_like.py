# Generated by Django 5.0.3 on 2024-05-08 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0004_remove_post_post_id_remove_post_post_photo_postphoto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='like',
            name='is_like',
        ),
    ]