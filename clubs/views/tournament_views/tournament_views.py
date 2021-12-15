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

from clubs.models import User, Tournament, Tournament_entry, Match, Membership
from clubs.forms import CreateTournamentForm
from clubs.helpers import required_role

from .tournament_methods import *


class CreateTournamentView(LoginRequiredMixin, FormView):
    template_name='create_tournament.html'
    model = Tournament
    form_class = CreateTournamentForm

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
    not_entered = Tournament.objects.exclude( creator = request.user ).exclude( tournament_entry__participant = request.user )
    return render(request, 'tournaments_list_view.html', {'created':created,'entered':entered, 'not_entered':not_entered})


@login_required
def join_tournament(request, tournament_id):
    if Tournament.objects.get( id = tournament_id).creator != request.user:
        try:
            tournament = Tournament.objects.get(id = tournament_id )
            newentry = Tournament_entry.objects.create(tournament = tournament, participant = request.user)
        except ObjectDoesNotExist:
            pass
    return redirect('tournaments_list_view')


@login_required
def leave_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get( id = tournament_id )
        entry_to_delete = Tournament_entry.objects.filter( tournament = tournament ).get( participant = request.user )
        if entry_to_delete:
            entry_to_delete.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('tournaments_list_view')


@required_role(Membership.OFFICER)
def manage_tournament(request, tournament_id):

    tournament_in = Tournament.objects.get( id = tournament_id )

    try:
        participants = set()
        for entry in Tournament_entry.objects.filter( tournament = tournament_in ).select_related('participant'):
            participants.add(entry.participant)
    except:
        participants = None
    try:
        matches = Match.objects.filter( tournament = tournament_in ).filter(winner = None)
    except:
        matches = None
    return render(request, "manage_tournament.html", {'tournament':tournament_in, "participants":participants,"matches":matches})


@required_role(Membership.OFFICER)
def schedule_matches(request, tournament_id):

    tournament = Tournament.objects.get( id = tournament_id )

    try :
        matches_check = Match.objects.filter( tournament = tournament )
        print(matches_check)
    except ObjectDoesNotExist:
        matches_check = None

    if matches_check == None or matches_check.count()==0:
        return initialize_matches(request, tournament_id)
    else:
        messages.error(request, "The matches have already been scheduled")
        return redirect('manage_tournament', tournament_id = tournament_id)


def initialize_matches(request, tournament_id):
    valid_entries_nos = [2,4,8,16,32]

    tournament = Tournament.objects.get( id = tournament_id )

    no_of_entries = Tournament_entry.objects.filter( tournament = tournament).count()
    if no_of_entries in valid_entries_nos:
        if no_of_entries == 32:
            participants = tournament.participants.all()
            generate_matches(participants, group_size = 4, stage = 5, tournament = tournament)
            return redirect('manage_tournament', tournament_id = tournament_id)
        else:
            participants = tournament.participants.all()
            n = participants.count()
            powtwo = 0
            while n>1:
                n/=2
                powtwo += 1
            generate_matches(participants, group_size = 2, stage = powtwo, tournament = tournament )
            return redirect('manage_tournament', tournament_id = tournament_id)
    else:
        messages.error(request, "The number of participants does not allow for a properly structured contest.")
        return redirect('manage_tournament', tournament_id  = tournament_id)


@login_required
def win_contender_one(request, match_id):
    match = Match.objects.get( id = match_id )
    match.winner = match.contender_one
    match.played = True
    match.save()

    go_to_next_stage_or_end_tournament(match_id)

    return redirect('manage_tournament', match.tournament.id)


@login_required
def win_contender_two(request,match_id):
    match = Match.objects.get( id = match_id )
    match.winner = match.contender_two
    match.played = True
    match.save()

    go_to_next_stage_or_end_tournament(match_id)

    return redirect('manage_tournament', match.tournament.id)

def draw_match(request, match_id):
    match = Match.objects.get(id = match_id)
    match.played = True
    match.save()

    if (match.stage < 5): # if the stage is smaller than 5, this was a knckout round, and another match is needed to establish who goes on to the next stage
        generate_draw_rematch(match_id)
    else:
        go_to_next_stage_or_end_tournament(match_id)

def generate_draw_rematch( match_id ):
    match = Match.objects.get( id = match_id )
    Match.objects.create( contender_one = match.contender_one, contender_two = match.contender_two, tournament = match.tournament, group = match.group, stage = match.stage )

def go_to_next_stage_or_end_tournament(match_id):
    match = Match.objects.get( id = match_id )
    if check_stage_is_done(match_id):
        if match.stage>1:
            setup_next_stage(match.tournament, match.stage)
        else:
            match.tournament.winner = match.winner
            match.tournament.save()

    return redirect('manage_tournament', match.tournament.id)
