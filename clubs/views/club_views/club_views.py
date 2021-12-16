"""Club related views."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView

from clubs.forms import CreateClubForm
from clubs.models import Club, Membership


class ClubListView(LoginRequiredMixin, ListView):
    """View that shows a list of all clubs, their details and their owner"""

    model = Club
    template_name = "club_list.html"
    context_object_name = "owners"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        clubs = Club.objects.all()
        owners = []
        for club in clubs:
            owners.append((club, club.membership_set.get(role=Membership.OWNER).user))
        return owners


class CreateClubView(LoginRequiredMixin, FormView):
    """View that creates a club."""

    form_class = CreateClubForm
    template_name = "create_club.html"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        membership = Membership(user=user, club=self.object, role=Membership.OWNER)
        membership.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('my_clubs')


class ShowClubView(DetailView):
    """View that show individual club details"""

    model = Club
    template_name = 'show_club.html'
    context_object_name = 'club'
    pk_url_kwarg = 'club_id'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['user'] = self.request.user
        return context

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('start')

"""view to apply for a club"""
@login_required
def apply_for_club(request, club_id):
    try:
        clubs = Club.objects.get(id=club_id)
        membership = Membership.objects.create(user=request.user, club=clubs)
        membership.save()
    except ObjectDoesNotExist:
        return redirect('my_clubs')
    return redirect('my_clubs')

"""view to leave a club"""
@login_required
def leave_club(request, club_id):
    try:
        club = Club.objects.get(id=club_id)
        user = request.user
        if not club.is_of_role(user, Membership.OWNER):
            membership = Membership.objects.get(user=user, club=club)
            membership.delete()
            if request.user.current_club == club:
                new_current_club = Club.objects.filter(membership__user=request.user).first()
                request.user.current_club = new_current_club
                request.user.save()
    except ObjectDoesNotExist:
        pass

    return redirect('my_clubs')

"""view to get list of clubs a user is in"""
@login_required
def my_clubs(request):
    user = request.user
    memberships = user.membership_set.all()
    clubs_user_in = []
    for membership in memberships:
        role = "Applicant"
        if membership.role == Membership.OWNER:
            role = "Owner"
        elif membership.role == Membership.OFFICER:
            role = "Officer"
        elif membership.role == Membership.MEMBER:
            role = "Member"
        clubs_user_in.append([membership.club, role])
    clubs_user_not_in = Club.objects.exclude(membership__user=user)
    return render(request, 'my_clubs.html', {'clubs_user_in': clubs_user_in, 'clubs_user_not_in': clubs_user_not_in})

"""view to switch between clubs"""
@login_required
def select_club(request, club_id):
    user = request.user
    try:
        club = Club.objects.get(id=club_id)
        if club.exist(user):
            user.select_club(club)
    except ObjectDoesNotExist:
        pass

    return redirect('start')
