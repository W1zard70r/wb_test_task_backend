import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Create or update a demo superuser for local Docker checks."

    def handle(self, *args, **options):
        username = os.getenv("DEMO_ADMIN_USERNAME", "admin")
        email = os.getenv("DEMO_ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("DEMO_ADMIN_PASSWORD", "admin12345")

        User = get_user_model()
        with transaction.atomic():
            user, created = User.objects.select_for_update().get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            changed_fields = []

            if user.email != email:
                user.email = email
                changed_fields.append("email")
            if not user.is_staff:
                user.is_staff = True
                changed_fields.append("is_staff")
            if not user.is_superuser:
                user.is_superuser = True
                changed_fields.append("is_superuser")
            if created or password:
                user.set_password(password)
                changed_fields.append("password")

            if changed_fields:
                user.save(update_fields=changed_fields)

        action = "created" if created else "ready"
        self.stdout.write(self.style.SUCCESS(f"Demo admin {action}: {username}"))
