from django.contrib import admin

from .models import User, Membership, Club, Tournament, Tournament_entry, Match


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

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for tournaments."""

    list_display = [
        'name','deadline','winner','capacity','club','creator'
    ]

@admin.register(Tournament_entry)
class TournamentEntryAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for tournament entries"""

    list_display = [
        'tournament', 'participant'
    ]

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for matches"""

    list_display = [
        'contender_one', 'contender_two', 'tournament', 'group', 'stage', 'winner'
    ]
