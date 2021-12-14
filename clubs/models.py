from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from libgravatar import Gravatar


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

    username = None
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    experience_level = models.CharField(max_length=520, blank=False)
    personal_statement = models.CharField(max_length=520, blank=False)

    current_club = models.ForeignKey('Club', null=True, on_delete=models.SET_NULL)

    def select_club(self, club):
        self.current_club = club
        self.save()

    @property
    def current_club_not_none(self):
        return self.current_club is not None

    @property
    def current_club_role(self):
        return self.current_club.membership_set.get(user=self).role

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='identicon')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=50)
    location = models.CharField(blank=False, max_length=50)
    mission_statement = models.CharField(blank=True, max_length=520)
    associates = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership')

    def add_user(self, user):
        self.associates.add(user)

    def exist(self, user):
        return self.membership_set.filter(user=user).exists()

    def is_of_role(self, user, role):
        return self.membership_set.get(user=user).role == role

    def change_role(self, user, new_role):
        try:
            membership = self.membership_set.get(user=user)
            membership.role = new_role
            membership.save()
        except ObjectDoesNotExist:
            pass

    @property
    def members_count(self):
        return self.associates.count()

    @property
    def owner(self):
        try:
            return self.associates.get(membership__role=Membership.OWNER)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return self.name


class Membership(models.Model):
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=APPLICANT)

    class Meta:
        db_table = 'membership'
        constraints = [
            models.UniqueConstraint(name='unique_role', fields=['user', 'club']),
            models.UniqueConstraint(name='one_owner_per_club', fields=['club', 'role'], condition=Q(role=3)),
            models.CheckConstraint(name='role_upperbound', check=models.Q(role__lte=3))
        ]
