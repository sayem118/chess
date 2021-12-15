"""Unit tests for the match model."""
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase

from clubs.models import User, Club, Membership, Tournament, Match


class MatchModelTestCase(TestCase):
    """Unit tests for the match model."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json',
        'clubs/tests/fixtures/tournaments/tournaments.json',
        'clubs/tests/fixtures/matches/matches.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.applicant = User.objects.get(email='jamiedoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.officer = User.objects.get(email='jamesdoe@example.org')
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.other_club = Club.objects.get(name='The Royal Rooks')
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        self.tournament = Tournament.objects.get(name="Chess Tournament")
        self.other_tournament = Tournament.objects.get(name="Battle of the Titans")
        self.match = Match.objects.get(contender_one=self.member)

    def test_valid_match(self):
        self._assert_match_is_valid()

    def test_contender_one_must_not_be_blank(self):
        self.match.contender_one = None
        self._assert_match_is_invalid()

    def test_contender_two_must_not_be_blank(self):
        self.match.contender_two = None
        self._assert_match_is_invalid()

    def test_tournament_must_not_be_blank(self):
        self.match.tournament = None
        self._assert_match_is_invalid()

    def test_group_must_not_be_blank(self):
        self.match.group = None
        self._assert_match_is_invalid()

    def test_stage_must_not_be_blank(self):
        self.match.stage = None
        self._assert_match_is_invalid()

    def test_winner_may_be_blank(self):
        self.winner = None
        self._assert_match_is_valid()

    def test_played_must_not_blank(self):
        self.played = None
        self._assert_match_is_invalid()

    def _assert_match_is_valid(self):
        try:
            self.match.full_clean()
        except ValidationError:
            self.fail('Test match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.match.full_clean()
