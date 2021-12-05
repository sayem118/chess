from django.core.management.base import BaseCommand

from clubs.models import User, Club


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Club.objects.all().delete()
