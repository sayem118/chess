"""Configuration of the admin interface for microblogs."""
from django.contrib import admin
from .models import Post, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""
    def group(self, User):
        groups = []
        for group in User.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groups'
    list_display = [
            'username', 'first_name', 'last_name', 'email', 'is_active','is_staff','group'
            ]



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for posts."""

    list_display = [
        'get_author', 'text', 'created_at',
    ]

    def get_author(self, post):
        """Return the author of a given post."""
        return post.author.username
