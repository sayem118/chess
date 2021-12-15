"""Unit tests for the Tournament entry model."""
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase

from clubs.models import User, Club, Membership, Tournament, Tournament_entry


class TournamentEntryModelTestCase(TestCase):
    """Unit tests for the Tournament entry model."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json',
        'clubs/tests/fixtures/tournaments/tournaments.json',
    ]

    def setUp(self):
        self.member = User.objects.get(email='janedoe@example.org')
        self.other_member = User.objects.get(email='janedoe@example.org')
        self.tournament = Tournament.objects.get(name="Chess Tournament")
        self.tournament_entry = Tournament_entry(participant=self.member, tournament=self.tournament)

    def test_valid_tournament_entry(self):
        self._assert_tournament_entry_is_valid()

    def test_participant_must_not_be_blank(self):
        self.tournament_entry.participant = None
        self._assert_tournament_entry_is_invalid()

    def test_tournament_must_not_be_blank(self):
        self.tournament_entry.tournament = None
        self._assert_tournament_entry_is_invalid()

    def _assert_tournament_entry_is_valid(self):
        try:
            self.tournament_entry.full_clean()
        except ValidationError:
            self.fail('Test Tournament Entry should be valid')

    def _assert_tournament_entry_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament_entry.full_clean()
