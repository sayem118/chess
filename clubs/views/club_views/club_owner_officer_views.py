"""Club owner related views."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from clubs.helpers import required_role
from clubs.models import User, Membership

"""a list to show all applicants"""
class ApplicantListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "approve_applicants.html"
    context_object_name = "applicants"
    paginate_by = settings.USERS_PER_PAGE

    @method_decorator(required_role(Membership.OFFICER))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        club = self.request.user.current_club
        applicants = club.associates.filter(membership__role=Membership.APPLICANT)
        return applicants

"""a list to display all members of the club"""
class MemberListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "promote_members.html"
    context_object_name = "members"
    paginate_by = settings.USERS_PER_PAGE

    @method_decorator(required_role(Membership.OWNER))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        club = self.request.user.current_club
        members = club.associates.filter(membership__role=Membership.MEMBER)
        return members

"""list to displau all officers of club"""
class OfficerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "manage_officers.html"
    context_object_name = "officers"
    paginate_by = settings.USERS_PER_PAGE

    @method_decorator(required_role(Membership.OWNER))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        club = self.request.user.current_club
        officers = club.associates.filter(membership__role=Membership.OFFICER)
        return officers

"""method for approving applications"""
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

"""method to promote users to officer"""
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

"""method to demote an officer"""
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

"""method to transfer ownership to another user"""
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
