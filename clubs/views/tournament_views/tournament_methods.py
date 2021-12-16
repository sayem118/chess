"""Tournament methods"""

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from clubs.models import Match, Tournament_entry, Tournament, User

import random

def generate_matches(participants, stage, tournament):
    # to add functionality that randomizes who ends up in which group

    aux_list = []
    randomized_participants = []

    for p in participants:
        aux_list.append(p)
    #print(aux_list)

    while len(aux_list):
        ind = random.randint(0, len(aux_list)-1)
        holder = aux_list[ind]
        aux_list.remove(holder)
        randomized_participants.append(holder)

    #print(randomized_participants)

    count = 0
    group_count = 0
    group_list = []

    group_size_list = []
    participant_list_length = len(randomized_participants)
    ind = 0

    if participant_list_length <= 16:
        divided_by_two = participant_list_length//2
        while divided_by_two > 0:
            group_size_list.append(2)
            divided_by_two -= 1
        if participant_list_length%2 == 1:
            group_size_list.append(1)
    else:
        divided_by_four = participant_list_length//4
        if participant_list_length%4 == 0:
            while divided_by_four > 0:
                group_size_list.append(4)
                divided_by_four -= 1
        elif participant_list_length%4 == 1:
            while divided_by_four > 0:
                group_size_list.append(4)
                divided_by_four -= 1
            group_size_list.append(1)
        elif participant_list_length%4 == 2:
            divided_by_four -= 2
            while divided_by_four > 0:
                 group_size_list.append(4)
                 divided_by_four -= 1
            group_size_list.append(3)
            group_size_list.append(3)
        else:
            while divided_by_four > 0:
                 group_size_list.append(4)
                 divided_by_four -= 1
            group_size_list.append(3)

    for p in randomized_participants:
        group_list.append(p)
        count += 1
        if count == group_size_list[group_count]:
            generate_matches_for_group( group_list, group_count, stage, tournament)
            group_count += 1
            group_list = []
            count = 0


def generate_matches_for_group( group_list, group_no, stage, tournament ):
    if len(group_list) == 1:
        Match.objects.create( contender_one = group_list[0], contender_two = group_list[0], tournament = tournament, group = group_no, stage = stage, winner = group_list[0], played = True)

    i = 0
    while i < len(group_list):
        j = i+1
        while j < len(group_list):
            Match.objects.create( contender_one = group_list[i], contender_two = group_list[j], tournament = tournament, group = group_no, stage = stage )
            j += 1
        i += 1


def check_stage_is_done(match_id):
    match = Match.objects.get( id = match_id )
    try:
        matches_in_stage = Match.objects.filter(tournament = match.tournament, stage = match.stage, played=False )
    except ObjectDoesNotExist:
        matches_in_stage = None

    if matches_in_stage == None or matches_in_stage.count()==0:
        return True
    else:
        return False


def setup_next_stage(tournament, last_stage):

    if check_for_and_generate_undecided_groups_of_three(tournament, last_stage):
        return redirect('manage_tournament', tournament_id)
    else:
        winners = get_winners( tournament, last_stage )
        generate_matches(winners, last_stage-1, tournament)

def check_for_and_generate_undecided_groups_of_three(tournament, stage):
    no_of_groups = Match.objects.filter(tournament = tournament).filter(stage = stage).values('group').distinct().count()

    group_id = 0

    found_undecided_flag = False

    while group_id < no_of_groups:
        user_score_dict = {}
        matches_in_group = Match.objects.filter(tournament = tournament).filter(stage = stage).filter(group = group_id).select_related('winner').select_related('contender_one').select_related('contender_two')
        if matches_in_group.count() != 3:
            pass
        else:
            participants = set()
            group_no = -1

            for m in matches_in_group:

                if group_no < 0:
                    group_no = m.group
                participants.add(m.contender_one)
                participants.add(m.contender_two)

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
            if len(set(user_score_dict.values())) == 1:
                participant_list = list(participants)
                generate_matches_for_group(participants_list, group_no, stage, tournament )
                found_undecided_flag = True
        group_id += 1

    return found_undecided_flag

def get_winners(tournament, stage):
    #First, get size of groups in stage
    """
    matches_in_a_group = Match.objects.filter(tournament = tournament).filter(stage = stage).filter(group = 0).select_related('contender_one').select_related('contender_two')
    contender_set = set()
    for m in matches_in_a_group:
        contender_set.add(m.contender_one)
        contender_set.add(m.contender_two)
    group_size = len(contender_set)
"""
    #if it is a knockout stage, it is easy to get the winners

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
                if m.contender_one == m.winner:
                    if not (m.contender_two.id in user_score_dict):
                        user_score_dict[m.contender_two.id] = 0
                else:
                    if not (m.contender_one.id in user_score_dict):
                        user_score_dict[m.contender_one.id] = 0

        greatest_score = -1
        second_greatest_score = -2
        first_winner_id = None
        second_winner_id = None
        for key in user_score_dict.keys():
            if  user_score_dict[key] > greatest_score :
                greatest_score = user_score_dict[key]
                first_winner_id = key
            elif user_score_dict[key] > second_greatest_score:
                second_greatest_score = user_score_dict[key]
                second_winner_id = key

        print( user_score_dict )
        print( len(user_score_dict.keys()) )
        print( first_winner_id )
        print (second_winner_id)

        if len(user_score_dict.keys()) > 2:

            winner_id_list.append(first_winner_id)
            winner_id_list.append(second_winner_id)
        else:
            winner_id_list.append(first_winner_id)

        group_id += 1

    winners = User.objects.filter(id__in=winner_id_list)
    return winners

"""
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
        """

def initialize_matches(request, tournament_id):
    powers_of_two = [2,4,8,16,32]

    tournament = Tournament.objects.get( id = tournament_id )

    no_of_entries = Tournament_entry.objects.filter( tournament = tournament).count()
    if no_of_entries >= 2 and no_of_entries <= 32:

        participants = tournament.participants.all()
        n = participants.count()
        powtwo = 0
        while n>1:
            n/=2
            powtwo += 1
        if n not in powers_of_two:
            powtwo += 1

        generate_matches(participants, stage = powtwo, tournament= tournament )

        return redirect('manage_tournament', tournament_id = tournament_id)
    else:
        if no_of_entries > 32:
            messages.error(request, "There are too many participants")
        else:
            message.error(request, "There are not enough participants")
        return redirect('manage_tournament', tournament_id  = tournament_id)


def generate_draw_rematch( match_id ):
    match = Match.objects.get( id = match_id )
    Match.objects.create( contender_one = match.contender_one, contender_two = match.contender_two, tournament = match.tournament, group = match.group, stage = match.stage )

def go_to_next_stage_or_end_tournament(match_id):
    match = Match.objects.get( id = match_id )
    if check_stage_is_done(match_id):
        print("stage is indeed done")
        if match.stage>1:
            setup_next_stage(match.tournament, match.stage)
        else:
            match.tournament.winner = match.winner
            match.tournament.save()

    return redirect('manage_tournament', match.tournament.id)
