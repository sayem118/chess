from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """Model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model used for authentication and clubs authoring."""
    APPLICANT = 0
    MEMBER = 1
    OFFICER = 2
    OWNER = 3

    ROLE_CHOICES = (
        (APPLICANT, 'Applicant'),
        (MEMBER, 'Member'),
        (OFFICER, 'Officer'),
        (OWNER, 'Owner'),
    )

    username = None
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    experience_level = models.CharField(max_length=520, blank=False)
    personal_statement = models.CharField(max_length=520, blank=False)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=APPLICANT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
