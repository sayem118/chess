from .models import Club


def get_clubs_user_belongs_to(request):
    user = request.user
    if user.is_authenticated:
        clubs = Club.objects.filter(membership__user=user)
        if user.current_club_not_none:
            clubs = clubs.exclude(id=user.current_club.id)

        return {
            'clubs_user_belongs_to': clubs
        }

    return {}
