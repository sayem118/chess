from django.conf import settings
from django.shortcuts import redirect

from clubs.models import User


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
            club = user.current_club
            if user.is_anonymous:
                return redirect('home')
            elif not club.is_of_role(user, role):
                return redirect('start')
            else:
                return view_function(request, *args, **kwargs)

        return modified_view_function

    return actual_decorator


def prohibited_role(role):
    def actual_decorator(view_function):
        def modified_view_function(request, *args, **kwargs):
            user = request.user
            club = user.current_club
            if user.is_anonymous:
                return redirect('home')
            elif club.is_of_role(user, role):
                return redirect('start')
            else:
                return view_function(request, *args, **kwargs)

        return modified_view_function

    return actual_decorator


def applicant_prohibited(view_function):
    def modified_view_function(request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('log_in')
        elif request.user.role == User.APPLICANT:
            return redirect('start')
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function
