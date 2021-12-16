from django.conf import settings
from django.shortcuts import redirect


def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function


def required_role(role):
    def actual_decorator(view_function):
        def modified_view_function(request, *args, **kwargs):
            user = request.user
            if user.is_anonymous:
                return redirect('log_in')
            if not user.current_club_not_none:
                return redirect('start')
            if user.current_club_role < role:
                return redirect('start')
            else:
                return view_function(request, *args, **kwargs)

        return modified_view_function

    return actual_decorator


def prohibited_role(role):
    def actual_decorator(view_function):
        def modified_view_function(request, *args, **kwargs):
            user = request.user
            if user.is_anonymous:
                return redirect('log_in')
            club = user.current_club
            if not user.current_club_not_none:
                return redirect('start')
            elif club.is_of_role(user, role):
                return redirect('start')
            else:
                return view_function(request, *args, **kwargs)

        return modified_view_function

    return actual_decorator
