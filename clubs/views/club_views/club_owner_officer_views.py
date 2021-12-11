"""Club owner related views."""

from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse

from clubs.models import User, Club, Membership
from clubs.forms import CreateClubForm
from clubs.helpers import required_role

@required_role(Membership.OFFICER)
def approve_applicant(request, user_id):
    try:
        old_role = Membership.APPLICANT
        new_role = Membership.MEMBER
        club = request.user.current_club
        user = User.objects.get(id=user_id)
        if club.exist(user) and club.is_of_role(user, old_role):
            club.change_role(user, new_role)
    except ObjectDoesNotExist:
        return redirect('start')
    else:
        return redirect('applicants_list')


@required_role(Membership.OWNER)
def members_list(request):
    club = request.user.current_club
    members = club.associates.filter(membership__role=Membership.MEMBER)
    return render(request, 'promote_members.html', {'members': members})


@required_role(Membership.OWNER)
def promote_member(request, user_id):
    try:
        old_role = Membership.MEMBER
        new_role = Membership.OFFICER
        club = request.user.current_club
        user = User.objects.get(id=user_id)
        if club.exist(user) and club.is_of_role(user, old_role):
            club.change_role(user, new_role)
    except ObjectDoesNotExist:
        return redirect('start')
    else:
        return redirect('members_list')


@required_role(Membership.OWNER)
def officers_list(request):
    club = request.user.current_club
    officers = club.associates.filter(membership__role=Membership.OFFICER)
    return render(request, 'manage_officers.html', {'officers': officers})


@required_role(Membership.OWNER)
def demote_officer(request, user_id):
    try:
        old_role = Membership.OFFICER
        new_role = Membership.MEMBER
        club = request.user.current_club
        user = User.objects.get(id=user_id)
        if club.exist(user) and club.is_of_role(user, old_role):
            club.change_role(user, new_role)
    except ObjectDoesNotExist:
        return redirect('start')
    else:
        return redirect('officers_list')


@required_role(Membership.OWNER)
def transfer_ownership(request, user_id):
    try:
        old_owner = request.user
        new_owner = User.objects.get(id=user_id)
        club = old_owner.current_club
        if club.exist(new_owner) and club.is_of_role(new_owner, Membership.OFFICER):
            club.change_role(old_owner, Membership.OFFICER)
            club.change_role(new_owner, Membership.OWNER)
    except ObjectDoesNotExist:
        return redirect('start')
    else:
        return redirect('start')


@required_role(Membership.OFFICER)
def applicants_list(request):
    club = request.user.current_club
    applicants = club.associates.filter(membership__role=Membership.APPLICANT)
    return render(request, 'approve_applicants.html', {'applicants': applicants})
