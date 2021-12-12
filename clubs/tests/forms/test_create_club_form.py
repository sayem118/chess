"""Unit tests of the create club form."""
from django import forms
from django.test import TestCase

from clubs.forms import CreateClubForm
from clubs.models import User, Club, Membership


class CreateClubFormTestCase(TestCase):
    """Unit tests of the create club form."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
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
        self.form_input = {
            'name': 'Test Club',
            'location': 'England',
            'mission_statement': 'This is the test club'
        }

    def test_valid_create_club_form(self):
        form = CreateClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('mission_statement', form.fields)
        name_field = form.fields['name']
        self.assertTrue(isinstance(name_field, forms.CharField))
        location_field = form.fields['location']
        self.assertTrue(isinstance(location_field, forms.CharField))
        mission_statement_field = form.fields['mission_statement']
        self.assertTrue(isinstance(mission_statement_field, forms.CharField))

    def test_club_name_cannot_be_blank(self):
        self.form_input['name'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_club_location_may_be_blank(self):
        self.form_input['location'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_club_mission_statement_cannot_be_blank(self):
        self.form_input['mission_statement'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_name_cannot_be_same_as_other_club(self):
        self.form_input['name'] = self.club.name
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateClubForm(data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        club = Club.objects.get(name='Test Club')
        self.assertEqual(club.location, 'England')
        self.assertEqual(club.mission_statement, 'This is the test club')
        self.assertTrue(form.is_valid())
