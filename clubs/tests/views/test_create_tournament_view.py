"""Tests of the create tournament view."""

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import datetime
from dateutil import tz

from clubs.forms import CreateTournamentForm
from clubs.models import User, Club, Membership, Tournament
from clubs.tests.helpers import reverse_with_next


class CreateTournamentViewTestCase(TestCase):
    """Tests of the create tournament view."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json',
        'clubs/tests/fixtures/tournaments/tournaments.json'
    ]

    def setUp(self):
        self.url = reverse('create_tournament')
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
            'name': 'Test Tournament',
            'description': 'This is a test tournament',
            'deadline': datetime(2024, 1, 2, 0, 0, 0, 0),
            'capacity': 90
        }

    def test_get_create_tournament_url(self):
        self.assertEqual(self.url, '/create_tournament/')

    def test_get_create_tournament(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tournament.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTournamentForm))
        self.assertFalse(form.is_bound)

    def test_get_create_tournament_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_create_tournaments_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_cannot_create_a_tournament_with_same_name(self):
        utc = tz.gettz('UTC')
        self.client.login(email=self.officer.email, password='Password123')
        self.form_input['name'] = 'Chess Tournament'
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tournament.html')
        club = Tournament.objects.get(name='Chess Tournament')
        self.assertNotEqual(club.description, 'This is a test tournament')
        self.assertNotEqual(club.deadline, datetime(2024, 1, 2, 0, 0, 0, 0, tzinfo=utc))
        self.assertNotEqual(club.capacity, 90)

    def test_successfully_create_a_tournament(self):
        utc = tz.gettz('UTC')
        self.client.login(email=self.officer.email, password='Password123')
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('tournaments_list_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournaments_list_view.html')
        tournament_to_check = Tournament.objects.get(name='Test Tournament')
        self.assertEqual(tournament_to_check.description, 'This is a test tournament')
        self.assertEqual(tournament_to_check.deadline, datetime(2024, 1, 2, 0, 0, tzinfo=utc))
        self.assertEqual(tournament_to_check.capacity, 90)
        self.assertEqual(tournament_to_check.creator, self.officer)
        self.assertEqual(tournament_to_check.club, self.other_club)
