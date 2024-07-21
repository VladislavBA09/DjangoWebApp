from django.contrib.auth import get_user_model
from social_core.exceptions import AuthException

User = get_user_model()


def associate_by_email(backend, details, user=None, *args, **kwargs):
    email = details.get('email')

    if user:
        return {'user': user}

    if email:
        try:
            existing_user = User.objects.get(email=email)
            return {'user': existing_user}
        except User.DoesNotExist:
            return None

    raise AuthException(backend, 'No email provided')


def save_user_email(sender=None, request=None, user=None, **kwargs):
    if user:
        email = user.email
        try:
            existing_user = User.objects.get(email=email)
            request.session['existing_user_id'] = existing_user.id
        except User.DoesNotExist:
            return "No existing user found with email."

    return {'user': user}
