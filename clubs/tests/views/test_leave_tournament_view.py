"""Tests of the leave tournament view."""

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from clubs.models import User, Club, Tournament, Tournament_entry
from clubs.tests.helpers import reverse_with_next


class LeaveTournamentViewTestCase(TestCase):
    """Tests of the leave tournament view."""

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
        self.tournament = Tournament.objects.get(name='Chess Tournament')
        self.other_tournament = Tournament.objects.get(name='Battle of the Titans')
        self.url = reverse('leave_tournament', kwargs={'tournament_id': self.tournament.id})

    def test_get_leave_tournament_url(self):
        self.assertEqual(self.url,f'/leave_tournament/{self.tournament.id}')

    def test_get_leave_tournament_with_invalid_id(self):
        self.client.login(email=self.owner.email, password='Password123')
        url = reverse('leave_tournament', kwargs={'tournament_id': self.tournament.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('tournaments_list_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournaments_list_view.html')

    def test_successful_leave_tournament(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('tournaments_list_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournaments_list_view.html')
        self.tournament.refresh_from_db()
        self.assertNotIn(self.member, self.tournament.participants.all())
        with self.assertRaises(ObjectDoesNotExist):
            Tournament_entry.objects.get(participant=self.member, tournament=self.tournament)

    def test_cannot_leave_if_not_in_tournament(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('tournaments_list_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournaments_list_view.html')
        self.tournament.refresh_from_db()
        self.assertNotIn(self.owner, self.tournament.participants.all())
        with self.assertRaises(ObjectDoesNotExist):
            Tournament_entry.objects.get(participant=self.owner, tournament=self.tournament)

    def test_cannot_leave_if_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('start')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')
        self.tournament.refresh_from_db()
        self.assertNotIn(self.applicant, self.tournament.participants.all())
        with self.assertRaises(ObjectDoesNotExist):
            Tournament_entry.objects.get(participant=self.applicant, tournament=self.tournament)
