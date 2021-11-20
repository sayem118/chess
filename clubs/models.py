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
