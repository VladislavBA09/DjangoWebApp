from uuid import uuid4

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.db.utils import OperationalError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .models import User
from .processor import query_database, send_email


class RegistrationView(View):

    def get(self, request):
        return render(request, 'registration.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmation_code = str(uuid4())
        confirm_password = request.POST.get('confirm_password')
        hashed_password = make_password(password)
        host = request.get_host()
        if password != confirm_password:
            return render(
                request,
                'registration.html',
                {'error': 'The passwords do not match. Try again.'}
            )
        if len(password) < 8:
            return render(
                request,
                'registration.html',
                {'error': 'Password must be at least 8 characters long.'}
            )
        if '@' not in email:
            return render(
                request,
                'registration.html',
                {'error': 'Email must contain the "@" symbol.'}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                'registration.html',
                {'error': 'User with this email already exists. '
                          'Please choose a different email.'}
            )

        user = User.objects.create(
            email=email,
            password=hashed_password,
            confirmation_code=confirmation_code,
            username=email
        )
        user.save()
        send_email(host, email, confirmation_code)

        return render(request, 'registration_done.html')


class ConfirmView(View):
    def get(self, request, code: str):
        user = User.objects.get(confirmation_code=code)
        user.confirmation = True
        user.save()
        return redirect(reverse('login_user'))


class LoginView(View):
    def get(self, request):
        return render(request, 'login_user.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if not user.confirmation:
                return render(request, 'login_user.html', {'error': 'User profile not verified'})
        except User.DoesNotExist:
            return render(request, 'login_user.html', {'error': 'There is no user with this email'})
        except OperationalError:
            return render(request, 'login_user.html', {'error': 'Database error'})

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            if not query_database(user.id):
                user.username = user.email
                user.save()
                return redirect(reverse('create_profile'))
            return redirect(reverse('home'))
        else:
            return render(request, 'login_user.html', {'error': 'Incorrect password'})
