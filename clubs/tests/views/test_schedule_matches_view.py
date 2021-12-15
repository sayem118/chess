"""Tests of the schedule matches view."""

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from clubs.models import User, Club, Membership, Tournament, Match
from clubs.tests.helpers import reverse_with_next


class ScheduleMatchesViewTestCase(TestCase):
    """Tests of the schedule matches view."""

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
        self.other_member = User.objects.get(email='janinedoe@example.org')
        self.officer = User.objects.get(email='jamesdoe@example.org')
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.other_club = Club.objects.get(name='The Royal Rooks')
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.other_member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        self.tournament = Tournament.objects.get(name='Chess Tournament')
        self.other_tournament = Tournament.objects.get(name='Battle of the Titans')
        self.url = reverse('schedule_matches', kwargs={'tournament_id': self.tournament.id})

    def test_get_schedule_matches_url(self):
        self.assertEqual(self.url, f'/schedule_matches/{self.tournament.id}')

    def test_get_schedule_matches_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_cannot_schedule_matches_when_not_officer(self):
        self.assert_redirects(self.applicant)
        self.assert_redirects(self.member)
        self.assert_redirects(self.owner)

    def test_get_successful_schedule_matches(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('manage_tournament', kwargs={'tournament_id': self.tournament.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_tournament.html')

    def test_cannot_schedule_matches_when_already_scheduled(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get(self.url)
        matches_before = Match.objects.filter(tournament=self.tournament)
        response = self.client.get(self.url, follow=True)
        matches_after = Match.objects.filter(tournament=self.tournament)
        self.assertEqual(len(matches_before), len(matches_after))
        redirect_url = reverse('manage_tournament', kwargs={'tournament_id': self.tournament.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_tournament.html')

    def test_cannot_schedule_matches_when_not_organiser(self):
        membership = Membership(user=self.user, club=self.other_club, role=Membership.OFFICER)
        membership.save()
        self.user.select_club(self.other_club)
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('manage_tournament', kwargs={'tournament_id': self.tournament.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_schedule_matches_with_invalid_id(self):
        self.client.login(email=self.officer.email, password='Password123')
        url = reverse('schedule_matches', kwargs={'tournament_id': self.tournament.id+9999})
        response = self.client.get(url, follow=True)
        redirect_url = reverse('tournaments_list_view')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournaments_list_view.html')

    def assert_redirects(self, test_user):
        if test_user:
            self.client.login(email=test_user.email, password='Password123')
        demote_view_url = reverse('schedule_matches', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(demote_view_url)
        start_url = reverse('start')
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)
