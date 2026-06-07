from django.urls import path

from apps.users.views import BalanceTopUpView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("me/balance/top-up/", BalanceTopUpView.as_view(), name="balance-top-up"),
]
