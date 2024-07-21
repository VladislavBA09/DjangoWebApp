from django.urls import path

from .views import ConfirmView, LoginView, RegistrationView


urlpatterns = [
    path('', RegistrationView.as_view(), name='registration'),
    path('confirm_registration/<str:code>/', ConfirmView.as_view(), name='confirm_registration'),
    path('login_user/', LoginView.as_view(), name='login_user'),
]