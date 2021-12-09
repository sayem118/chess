from django.contrib import admin

from .models import User, Membership, Club


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'first_name', 'last_name', 'email', 'experience_level'
    ]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'name','location'
    ]

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'user','club','role'
    ]
