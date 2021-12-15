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
    match.played = True
    match.save()

    go_to_next_stage_or_end_tournament(match_id)

    return redirect('manage_tournament', match.tournament.id)

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

def check_stage_is_done(match_id):
    match = Match.objects.get( id = match_id )
    try:
        matches_not_played = Match.objects.filter(tournament = match.tournament).filter(stage = match.stage).filter( played = False )
    except ObjectDoesNotExist:
        matches_in_stage = None

    if matches_not_played == None or matches_not_played.count()==0:
        print("stage is done")
        return True
    else:
        print("Stage is not done")
        return False


def setup_next_stage(tournament, last_stage):

    winners = get_winners( tournament, last_stage )

    if (last_stage-1 < 5):
        generate_matches(winners, 2, last_stage-1, tournament)
    else:
        #no_of_participants = Tournament_entry.objects.filter( tournament = tournament ).count()
        #if no_of_participants > 16 and no_of_participants<=32:
        generate_matches(winners, 4, last_stage-1, tournament)

def get_winners(tournament, stage):
    #First, get size of groups in stage
    matches_in_a_group = Match.objects.filter(tournament = tournament).filter(stage = stage).filter(group = 0).select_related('contender_one').select_related('contender_two')
    contender_set = set()
    for m in matches_in_a_group:
        contender_set.add(m.contender_one)
        contender_set.add(m.contender_two)
    group_size = len(contender_set)

    #if it is a knockout stage, it is easy to get the winners
    if group_size == 2:
        matches = Match.objects.filter(tournament = tournament).filter(stage = stage)
        winner_id_list = []
        for m in matches:
            winner_id_list.append(m.winner.id)
        winners = User.objects.filter(id__in=winner_id_list)
        return winners

    #Secondly, get number of groups
    no_of_groups = Match.objects.filter(tournament = tournament).filter(stage = stage).values('group').distinct().count()

    #Then, go through each group and get the two winners based on match outcomes
    group_id = 0
    winner_id_list = []
    while group_id < no_of_groups:
        user_score_dict = {}
        matches_in_group = Match.objects.filter(tournament = tournament).filter(stage = stage).filter(group = group_id).select_related('winner').select_related('contender_one').select_related('contender_two')
        for m in matches_in_group:
            if m.winner == None:
                if not( m.contender_one.id in user_score_dict ):
                    user_score_dict[m.contender_one.id] = 0
                user_score_dict[m.contender_one.id]+=0.5
                if not( m.contender_two.id in user_score_dict ):
                    user_score_dict[m.contender_two.id] = 0
                user_score_dict[m.contender_two.id]+=0.5
            else:
                if not (m.winner.id in user_score_dict):
                    user_score_dict[m.winner.id] = 0
                user_score_dict[m.winner.id]+=1

        greatest_score = -1
        second_greatest_Score = -2
        first_winner_id = None
        second_winner_id = None
        for key in user_score_dict.keys():
            if  user_score_dict[key] > greatest_score :
                greatest_score = user_score_dict[key]
                first_winner_id = key
            elif user_score_dict[key] > second_greatest_Score:
                second_greatest_Score = user_score_dict[key]
                second_winner_id = key

        winner_id_list.append(first_winner_id)
        winner_id_list.append(second_winner_id)

        group_id += 1

    winners = User.objects.filter(id__in=winner_id_list)
    return winners
