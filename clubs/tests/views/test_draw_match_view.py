"""Tests of the draw match view."""

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from clubs.models import User, Club, Membership, Tournament, Match
from clubs.tests.helpers import reverse_with_next


class DrawMatchViewTestCase(TestCase):
    """Tests of the draw match view."""

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
        self.match = Match(contender_one=self.member, contender_two=self.other_member, tournament=self.tournament, group=1, stage=5)
        self.match.save()
        self.url = reverse('draw_match', kwargs={'match_id': self.match.id})

    def test_get_draw_match_url(self):
        self.assertEqual(self.url, f'/draw_match/{self.match.id}')

    def test_draw_match_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_draw_match_when_not_knockout(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('manage_tournament', kwargs={'tournament_id': self.tournament.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_tournament.html')
        self.match.refresh_from_db()
        self.assertEqual(self.match.winner, None)
        self.assertTrue(self.match.played)

    def test_successful_draw_match_when_knockout(self):
        self.match.stage = 1
        self.match.save()
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('manage_tournament', kwargs={'tournament_id': self.tournament.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_tournament.html')
        self.match.refresh_from_db()
        try:
            new_match = Match.objects.get(contender_one=self.member, contender_two=self.other_member, played=False)
            self.assertEqual(new_match.stage, self.match.stage)
            self.assertEqual(new_match.group, self.match.group)
        except ObjectDoesNotExist:
            self.fail('A new match should be scheduled')
        self.assertEqual(self.match.winner, None)
        self.assertTrue(self.match.played)

    def test_draw_match_with_invalid_id(self):
        self.client.login(email=self.officer.email, password='Password123')
        url = reverse('draw_match', kwargs={'match_id': self.match.id+9999})
        response = self.client.get(url, follow=True)
        redirect_url = reverse('start')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')
