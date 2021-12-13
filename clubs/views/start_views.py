from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from clubs.forms import CreateClubForm
from clubs.models import Club


class StartView(LoginRequiredMixin, ListView):
    """Class-based generic view for displaying a view."""

    model = Club
    template_name = "start.html"
    context_object_name = "clubs"
    paginate_by = settings.CLUBS_PER_PAGE

    def get_queryset(self):
        """Return all existing clubs."""
        clubs = list(Club.objects.all())
        return clubs

    def get_context_data(self, **kwargs):
        """Return context data, including new club form."""
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["form"] = CreateClubForm()
        return context
