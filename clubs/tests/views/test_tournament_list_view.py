"""Test of the tournament list view"""

from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin

from clubs.models import User, Club, Tournament
from clubs.tests.helpers import reverse_with_next


class TournamentListTest(TestCase,AssertHTMLMixin):
    """Test of the tournament list view"""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json',
        'clubs/tests/fixtures/tournaments/tournaments.json'
    ]

    def setUp(self):
        self.url = reverse('tournaments_list_view')
        self.user = User.objects.get(email='johndoe@example.org')
        self.applicant = User.objects.get(email='jamiedoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.officer = User.objects.get(email="jamesdoe@example.org")
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.other_club = Club.objects.get(name='The Royal Rooks')
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        self.tournament = Tournament.objects.get(name='Chess Tournament')
        self.other_tournament = Tournament.objects.get(name='Battle of the Titans')

    def test_tournament_list_url(self):
        self.assertEqual(self.url, '/tournaments_list_view/')

    def test_club_list_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_is_accessible_to_all_member_roles(self):
        self.assert_accessible(self.member)
        self.assert_accessible(self.officer)
        self.assert_accessible(self.owner)

    def test_not_accessible_to_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('start')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')
        self.assertNotContains(response, self.tournament.name)
        self.assertNotContains(response, self.other_tournament.name)

    def test_not_accessable_with_no_club_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('start')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')
        self.assertNotContains(response, self.tournament.name)
        self.assertNotContains(response, self.other_tournament.name)

    def test_not_accessable_for_user_who_is_not_in_any_club(self):
        User.objects.create_user(email='test@example.org', password='Password123')
        test_user = User.objects.get(email='test@example.org')
        self.client.login(email=test_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('start')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')
        self.assertNotContains(response, self.tournament.name)
        self.assertNotContains(response, self.other_tournament.name)

    def assert_accessible(self, test_user):
        self.client.login(email=test_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournaments_list_view.html')
        self.assertContains(response, self.tournament.name)
        self.assertNotContains(response, self.other_tournament.name)
