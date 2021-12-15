"""Unit tests of the create tournament form."""
from django import forms
from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from dateutil import tz

from clubs.forms import CreateTournamentForm
from clubs.models import User, Club, Membership, Tournament


class CreateTournamentFormTestCase(TestCase):
    """Unit tests of the create tournament form."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json',
        'clubs/tests/fixtures/tournaments/tournaments.json'
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
        self.form_input = {
            'name': 'Test Tournament',
            'description': 'This is a test tournament',
            'deadline': datetime(2024, 1, 1, 0, 0, 0, 0),
            'capacity': 96
        }

    def test_valid_create_tournament_form(self):
        form = CreateTournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateTournamentForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('deadline', form.fields)
        self.assertIn('capacity', form.fields)
        name_field = form.fields['name']
        self.assertTrue(isinstance(name_field, forms.CharField))
        description_field = form.fields['description']
        self.assertTrue(isinstance(description_field, forms.CharField))
        deadline_field = form.fields['deadline']
        self.assertTrue(isinstance(deadline_field, forms.DateTimeField))
        capacity_field = form.fields['capacity']
        self.assertTrue(isinstance(capacity_field, forms.IntegerField))

    def test_tournament_name_cannot_be_blank(self):
        self.form_input['name'] = ''
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_tournament_description_may_be_blank(self):
        self.form_input['description'] = ''
        form = CreateTournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_tournament_deadline_cannot_be_blank(self):
        self.form_input['deadline'] = None
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_tournament_capacity_cannot_be_blank(self):
        self.form_input['capacity'] = None
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_name_cannot_be_same_as_other_tournament(self):
        self.form_input['name'] = self.tournament.name
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        utc = tz.gettz('UTC')
        form = CreateTournamentForm(data=self.form_input)
        form.instance.club = self.other_club
        form.instance.creator = self.officer
        before_count = Tournament.objects.count()
        form.save()
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        tournament = Tournament.objects.get(name='Test Tournament')
        self.assertEqual(tournament.description, 'This is a test tournament')
        self.assertEqual(tournament.deadline, datetime(2024, 1, 1, 0, 0, tzinfo=utc))
        self.assertEqual(tournament.capacity, 96)
        self.assertTrue(form.is_valid())
