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


def officer_only(view_function):
    def modified_view_function(request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('home')
        elif request.user.role != User.OFFICER:
            return redirect('start')
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function


def permission_required(required_role):
    def actual_decorator(view_function):
        def modified_view_function(request, *args, **kwargs):
            if request.user.is_anonymous:
                return redirect('home')
            elif request.user.role != required_role:
                return redirect('start')
            else:
                return view_function(request, *args, **kwargs)
        return modified_view_function
    return actual_decorator
