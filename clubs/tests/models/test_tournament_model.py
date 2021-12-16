"""Unit tests for the Tournament model."""
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase

from clubs.models import User, Club, Membership, Tournament


class TournamentModelTestCase(TestCase):
    """Unit tests for the Tournament model."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json',
        'clubs/tests/fixtures/tournaments/tournaments.json',
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

    def test_valid_tournament(self):
        self._assert_tournament_is_valid()

    def test_name_must_not_be_blank(self):
        self.tournament.name = ''
        self._assert_tournament_is_invalid()

    def test_name_must_be_unique(self):
        self.tournament.name = self.other_tournament.name
        self._assert_tournament_is_invalid()

    def test_name_may_contain_100_characters(self):
        self.tournament.name = 'x' * 100
        self._assert_tournament_is_valid()

    def test_name_must_not_contain_more_than_100_characters(self):
        self.tournament.name = 'x' * 101
        self._assert_tournament_is_invalid()

    def test_description_may_be_blank(self):
        self.tournament.description = ''
        self._assert_tournament_is_valid()

    def test_description_may_not_be_unique(self):
        self.tournament.description = self.other_tournament.description
        self._assert_tournament_is_valid()

    def test_description_may_contain_500_characters(self):
        self.tournament.description = 'x' * 500
        self._assert_tournament_is_valid()

    def test_description_must_not_contain_more_than_500_characters(self):
        self.tournament.description = 'x' * 501
        self._assert_tournament_is_invalid()

    def test_club_must_not_be_blank(self):
        self.tournament.club = None
        self._assert_tournament_is_invalid()

    def test_deadline_must_not_be_blank(self):
        self.tournament.deadline = None
        self._assert_tournament_is_invalid()

    def test_creator_must_not_be_blank(self):
        self.tournament.creator = None
        self._assert_tournament_is_invalid()

    def test_capacity_must_not_be_blank(self):
        self.tournament.capacity = None
        self._assert_tournament_is_invalid()

    def test_capacity_must_not_be_negative(self):
        self.tournament.capacity = -1
        self._assert_tournament_is_invalid()

    def test_capacity_can_be_up_to_96(self):
        self.tournament.capacity = 96
        self._assert_tournament_is_valid()

    def test_capacity_must_not_be_greater_than_96(self):
        self.tournament.capacity = 97
        self._assert_tournament_is_invalid()

    def test_winner_may_be_blank(self):
        self.tournament.winner = None
        self._assert_tournament_is_valid()

    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except ValidationError:
            self.fail('Test Tournament should be valid')

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
