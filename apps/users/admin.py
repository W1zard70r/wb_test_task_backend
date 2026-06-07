from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Marketplace", {"fields": ("balance",)}),
    )
    list_display = ("id", "username", "email", "balance", "is_staff")
