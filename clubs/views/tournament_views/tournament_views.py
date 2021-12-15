"Tournament related views"

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.db.models import F
from django.utils.decorators import method_decorator

from clubs.models import User, Tournament, Tournament_entry, Match, Membership, Club
from clubs.forms import CreateTournamentForm
from clubs.helpers import required_role

from .tournament_methods import *


class CreateTournamentView(LoginRequiredMixin, FormView):
    template_name='create_tournament.html'
    model = Tournament
    form_class = CreateTournamentForm

    @method_decorator(required_role(Membership.OFFICER))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.club = self.request.user.current_club
        form.instance.creator = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tournaments_list_view')

@login_required
def tournaments_list_view(request):
    created = Tournament.objects.filter( creator = request.user )
    entered = Tournament.objects.exclude( creator = request.user ).filter( tournament_entry__participant = request.user )
    clubs_full_member_of = Club.objects.filter( membership__user = request.user, membership__role__in = [Membership.MEMBER, Membership.OFFICER, Membership.OWNER] )
    not_entered = Tournament.objects.exclude( creator = request.user ).exclude( tournament_entry__participant = request.user ).filter( club__in = clubs_full_member_of )
    return render(request, 'tournaments_list_view.html', {'created':created,'entered':entered, 'not_entered':not_entered})


@login_required
def join_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id = tournament_id )
        if tournament.creator != request.user:
            if Membership.objects.filter( club = tournament.club, user = request.user, role__in = [Membership.MEMBER, Membership.OFFICER, Membership.OWNER] ).count() == 1:
                newentry = Tournament_entry.objects.create(tournament = tournament, participant = request.user)
            else:
                messages.error(request, "You cannot take part in a tournament from a club you're not a full member of")
                return redirect('tournaments_list_view')
        else:
            messages.error(request, "You cannot take part in a tournament you created")
            return redirect('tournaments_list_view')
    except ObjectDoesNotExist:
        pass
    return redirect('tournaments_list_view')


@login_required
def leave_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get( id = tournament_id )
        entry_to_delete = Tournament_entry.objects.filter( tournament = tournament ).get( participant = request.user )
        entry_to_delete.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('tournaments_list_view')


@required_role(Membership.OFFICER)
def manage_tournament(request, tournament_id):

    tournament_in = None
    try:
        tournament_in = Tournament.objects.get( id = tournament_id )
    except ObjectDoesNotExist:
        return redirect('tournaments_list_view')
    try:
        participants = set()
        for entry in Tournament_entry.objects.filter( tournament = tournament_in ).select_related('participant'):
            participants.add(entry.participant)
    except ObjectDoesNotExist:
        participants = None
    try:
        matches = Match.objects.filter( tournament = tournament_in ).filter(played = False)
    except ObjectDoesNotExist:
        matches = None
    return render(request, "manage_tournament.html", {'tournament':tournament_in, "participants":participants,"matches":matches})


@required_role(Membership.OFFICER)
def schedule_matches(request, tournament_id):

    tournament = None
    try:
        tournament = Tournament.objects.get( id = tournament_id )
    except ObjectDoesNotExist:
        return redirect('tournaments_list_view')
    matches_check = Match.objects.filter( tournament = tournament )
    if matches_check.count()==0:
        return initialize_matches(request, tournament_id)
    else:
        messages.error(request, "The matches have already been scheduled")
        return redirect('manage_tournament', tournament_id = tournament_id)


@login_required
def win_contender_one(request, match_id):
    try:
        match = Match.objects.get( id = match_id )
        match.winner = match.contender_one
        match.played = True
        match.save()
        go_to_next_stage_or_end_tournament(match_id)
        return redirect('manage_tournament', match.tournament.id)
    except ObjectDoesNotExist:
        return redirect('start')


@login_required
def win_contender_two(request, match_id):
    try:
        match = Match.objects.get( id = match_id )
        match.winner = match.contender_two
        match.played = True
        match.save()
        go_to_next_stage_or_end_tournament(match_id)
        return redirect('manage_tournament', match.tournament.id)
    except ObjectDoesNotExist:
        return redirect('start')

@login_required
def draw_match(request, match_id):
    try:
        match = Match.objects.get(id = match_id)
        match.played = True
        match.save()
        if ( is_knockout_round(match_id )): # if the stage is smaller than 5, this was a knckout round, and another match is needed to establish who goes on to the next stage
            generate_draw_rematch(match_id)
        else:
            go_to_next_stage_or_end_tournament(match_id)
        return redirect('manage_tournament', match.tournament.id)
    except ObjectDoesNotExist:
        return redirect('start')

def is_knockout_round( match_id ):
    match = Match.objects.get( id = match_id)

    matches_in_group = Match.objects.filter(tournament = match.tournament).filter(stage = match.stage).filter(group = match.group).select_related('contender_one').select_related('contender_two')

    participants = set()

    for m in matches_in_group:
        participants.add(m.contender_one)
        participants.add(m.contender_two)

    if len(participants) == 2:
        print( " is indeed a knockout" )
        return True
    else:
        return False
