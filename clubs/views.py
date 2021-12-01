from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic import ListView

from .forms import LogInForm, SignUpForm, UserForm, PasswordForm
from .helpers import login_prohibited, officer_only, applicant_prohibited
from .models import User


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
    """View that shows indiviual user details"""

    model = User
    template_name = 'show_user.html'
    context_object_name = "user"
    pk_url_kwarg = 'user_id'

    @method_decorator(login_required)
    @method_decorator(applicant_prohibited)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template"""

        context = super().get_context_data(*args, **kwargs)
        user = self.get_object()
        context['is_staff'] = self.request.user.role in {User.OFFICER, User.OWNER}
        return context

    def get(self, request, *args, **kwargs):
        """handle get request, and redirect to user_list if user_id invalid"""

        try:
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

    @method_decorator(applicant_prohibited)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if self.request.user == User.MEMBER:
            return User.objects.filter(role = User.MEMBER)
        else:
            return User.objects.exclude(role = User.APPLICANT)


@login_required
def start(request):
    return render(request, 'start.html')


@login_required
def member_status(request):
    current_user = request.user
    if current_user.role == User.APPLICANT:
        return render(request, 'applicant_status.html')
    elif current_user.role == User.MEMBER:
        return render(request, 'member_status.html')
    elif current_user.role == User.OFFICER:
        return render(request, 'officer_status.html')
        # applicants = User.objects.filter(role=User.APPLICANT)
        # return render(request, 'accept_applicants.html', {'applicants': applicants})
    elif current_user.role == User.OWNER:
        return render(request, 'owner_status.html')


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


@officer_only
def applicants_list(request):
    applicants = User.objects.filter(role=User.APPLICANT)
    return render(request, 'accept_applicants.html', {'applicants': applicants})


@officer_only
def approve_applicant(request, user_id):
    try:
        applicant = User.objects.get(id=user_id)
        if applicant.role == User.APPLICANT:
            applicant.role = User.MEMBER
            applicant.save()
    except ObjectDoesNotExist:
        return redirect('start')
    else:
        return redirect('applicants_list')
