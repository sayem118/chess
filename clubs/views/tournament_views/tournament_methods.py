"""Tournament methods"""

from django.core.exceptions import ObjectDoesNotExist

from clubs.models import Match


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

    # to modify thing in generate matches to be like this lmao
    generate_matches(winners, 2, last_stage-1, tournament)
