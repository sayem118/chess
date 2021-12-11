"""Club related views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.http import Http404
from django.shortcuts import redirect, render
from django.shortcuts import redirect
from django.urls import reverse

from clubs.helpers import required_role, user_has_to_be_apart_of_a_club
from clubs.models import User, Club, Membership
from clubs.forms import CreateClubForm


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


class MemberStatusView(LoginRequiredMixin, ListView):
    """View that shows the memberships of all the clubs the user is apart of"""

    model = Club
    template_name = "member_status.html"
    context_object_name = "clubs"

    @method_decorator(user_has_to_be_apart_of_a_club)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        memberships = user.membership_set.all()
        clubs = []
        for membership in memberships:
            role = "Applicant"
            if membership.role == Membership.OWNER:
                role = "Owner"
            elif membership.role == Membership.OFFICER:
                role = "Officer"
            elif membership.role == Membership.MEMBER:
                role = "Member"
            clubs.append([membership.club, role])
        return clubs


@required_role(Membership.OFFICER)
def applicants_list(request):
    club = request.user.current_club
    applicants = club.associates.filter(membership__role=Membership.APPLICANT)
    return render(request, 'approve_applicants.html', {'applicants': applicants})


@login_required
def apply_for_club(request, club_id):
    try:
        clubs = Club.objects.get(id=club_id)
        membership = Membership.objects.create(user=request.user, club=clubs)
        membership.save()
    except ObjectDoesNotExist:
        return redirect('my_clubs')
    return redirect('my_clubs')


@login_required
def leave_club(request, club_id):
    try:
        clubs = Club.objects.get(id=club_id)
        user_id = request.user.id
        if request.user.current_club == clubs:
            membership = Membership.objects.get(user=user_id, club=clubs)
            membership.delete()
            MyClubs = Club.objects.filter(membership__user=request.user).first()
            request.user.current_club = MyClubs
            request.user.save()
        else:
            membership = Membership.objects.get(user=user_id, club=clubs)
            membership.delete()
    except ObjectDoesNotExist:
        pass

    return redirect('my_clubs')


@login_required
def my_clubs(request):
    user = request.user
    MyClubs = Club.objects.filter(membership__user=user)
    NotMyClubs = Club.objects.exclude(membership__user=user)
    return render(request, 'my_clubs.html', {'MyClubs': MyClubs, 'NotMyClubs': NotMyClubs})


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
