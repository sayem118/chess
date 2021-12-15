from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormView

from django.views.generic.edit import CreateView
from django.contrib import messages
from django.db.models import F
from clubs.models import User, Membership, Tournament, Tournament_entry, Match
from clubs.forms import CreateTournamentForm
from clubs.helpers import required_role

"""to add try"""
def tournaments_list_view(request):
    created = Tournament.objects.filter( creator = request.user )
    entered = Tournament.objects.exclude( creator = request.user ).filter( tournament_entry__participant = request.user )
    not_entered = Tournament.objects.exclude( creator = request.user ).exclude( tournament_entry__participant = request.user )
    return render(request, 'tournaments_list_view.html', {'created':created,'entered':entered, 'not_entered':not_entered})

@login_required
def join_tournament(request, tournament_id):
    if Tournament.objects.get( id = tournament_id).creator == request.user:
        redirect('tournaments_list_view')
    else:
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


class CreateTournamentView(LoginRequiredMixin, FormView):
    template_name='create_tournament.html'
    model = Tournament
    form_class = CreateTournamentForm

    def form_valid(self, form):
        print(f'current club{ self.request.user.current_club }')
        form.instance.club = self.request.user.current_club
        form.instance.creator = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tournaments_list_view')

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


def generate_matches(participants, group_size, stage, tournament):
    # to add functionality that randomizes who ends up in which group
    count = 0
    group_count = 0
    group_list = []
    for p in participants:
        group_list.append(p)
        count += 1
        if count == group_size:
            generate_matches_for_group( group_list, group_count, stage, tournament)
            group_count += 1
            group_list = []
            count = 0

def generate_matches_for_group( group_list, group_no, stage, tournament ):
    i = 0
    while i < len(group_list):
        j = i+1
        while j < len(group_list):
            Match.objects.create( contender_one = group_list[i], contender_two = group_list[j], tournament = tournament, group = group_no, stage = stage )
            j += 1
        i += 1

def win_contender_one(request, match_id):
    match = Match.objects.get( id = match_id )
    match.winner = match.contender_one
    match.save()

    if check_stage_is_done(match_id):
        if match.stage>1:
            setup_next_stage(match.tournament, match.stage)
        else:
            match.tournament.winner = match.winner
            match.tournament.save()

    return redirect('manage_tournament', match.tournament.id)

def win_contender_two(request,match_id):
    match = Match.objects.get( id = match_id )
    match.winner = match.contender_two
    match.save()

    if check_stage_is_done(match_id):
        if match.stage>1:
            setup_next_stage(match.tournament, match.stage)
        else:
            match.tournament.winner = match.winner
            match.tournament.save()

    return redirect('manage_tournament', match.tournament.id)

def check_stage_is_done(match_id):
    match = Match.objects.get( id = match_id )
    try:
        matches_in_stage = Match.objects.filter(tournament = match.tournament).filter(stage = match.stage).filter(winner__isnull=True )
    except ObjectDoesNotExist:
        matches_in_stage = None

    if matches_in_stage == None or matches_in_stage.count()==0:
        return True
    else:
        return False

def setup_next_stage(tournament, last_stage):

    #winners = User.objects.filter(matches_won__tournament = tournament).filter(matches_won__stage = last_stage)
    matches_last_stage = Match.objects.filter(tournament = tournament).filter(stage = last_stage)
    winner_id_list = []
    for m in matches_last_stage:
        winner_id_list.append(m.winner.id)
    winners = User.objects.filter(id__in=winner_id_list)

    print(winners)
    # to modify thing in generate matches to be like this lmao
    generate_matches(winners, 2, last_stage-1, tournament)
