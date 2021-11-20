from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """User model used for authentication and clubs authoring."""
    APPLICANT = 0
    MEMBER = 1
    OFFICER = 2
    OWNER = 3

    ROLE_CHOICES = (
        (APPLICANT, 'Applicant'),
        (MEMBER, 'Member'),
        (OFFICER,'Officer'),
        (OWNER,'Owner'),
    )

    username = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    role = models.PositiveSmallIntegerField(choices = ROLE_CHOICES, default = APPLICANT)
#jacky12 = User.objects.create_user(username = 'jack234y23@gmail.com', first_name = 'john', last_name = 'doe', password = 'Password123', bio = 'hi i hope this works', role = 2)
