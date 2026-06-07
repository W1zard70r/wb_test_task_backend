from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Marketplace", {"fields": ("balance",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Marketplace", {"fields": ("email", "balance")}),
    )
    list_display = ("id", "username", "email", "balance", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)
