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

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    role = models.PositiveSmallIntegerField(choices = ROLE_CHOICES, default = APPLICANT)
