"""User related views."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from clubs.helpers import prohibited_role
from clubs.models import User, Membership


class ShowUserView(DetailView):
    """View that shows individual user details"""

    model = User
    template_name = 'show_user.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'

    @method_decorator(login_required)
    @method_decorator(prohibited_role(Membership.APPLICANT))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template"""

        context = super().get_context_data(*args, **kwargs)
        context['user'] = self.request.user
        context['user_to_view'] = self.get_object()
        context['is_staff'] = self.request.user.current_club_not_none and self.request.user.current_club_role in {
            Membership.OFFICER, Membership.OWNER}
        return context

    def get(self, request, *args, **kwargs):
        """handle get request, and redirect to user_list if user_id invalid"""
        try:
            if self.request.user.current_club_role == Membership.MEMBER:
                if self.request.user.current_club.membership_set.get(user=self.get_object()).role in {
                        Membership.OFFICER, Membership.OWNER}:
                    return redirect('user_list')
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('user_list')


class UserListView(LoginRequiredMixin, ListView):
    """View that shows a list of all users"""

    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    paginate_by = settings.USERS_PER_PAGE

    @method_decorator(prohibited_role(Membership.APPLICANT))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        club = user.current_club
        if user.current_club_role == Membership.MEMBER:
            return club.associates.filter(membership__role=Membership.MEMBER)
        return club.associates.exclude(membership__role=Membership.APPLICANT)
