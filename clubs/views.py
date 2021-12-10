from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from .forms import LogInForm, SignUpForm, UserForm, PasswordForm, CreateClubForm
from .helpers import login_prohibited, required_role, prohibited_role, user_has_to_be_apart_of_a_club
from .models import User, Membership, Club


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in"""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirects when logged in or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def get_redirect_when_logged_in_url(self):
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'"
            )
        else:
            return self.redirect_when_logged_in_url

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)


class ShowUserView(DetailView):
    """View that shows individual user details"""

    model = User
    template_name = 'show_user.html'
    context_object_name = "user"
    pk_url_kwarg = 'user_id'

    @method_decorator(login_required)
    @method_decorator(prohibited_role(Membership.APPLICANT))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template"""

        context = super().get_context_data(*args, **kwargs)
        context['user'] = self.get_object()
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


class LogInView(LoginProhibitedMixin, View):
    """View that handles log in"""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'start'

    def get(self, request):
        """Display log in template"""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt"""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form"""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


class SignUpView(LoginProhibitedMixin, FormView):
    """View that signs up user."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


@login_prohibited
def home(request):
    logout(request)
    return render(request, 'home.html')


def log_out(request):
    logout(request)
    return redirect('home')


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


@login_required
def start(request):
    return render(request, 'start.html')


@login_required
def profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('start')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'profile.html', {'form': form})


@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('start')
    form = PasswordForm()
    return render(request, 'password.html', {'form': form})


@required_role(Membership.OFFICER)
def applicants_list(request):
    club = request.user.current_club
    applicants = club.associates.filter(membership__role=Membership.APPLICANT)
    return render(request, 'approve_applicants.html', {'applicants': applicants})


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
