"""Test of the club list view"""

from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin

from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class ClubListTest(TestCase,AssertHTMLMixin):

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse('club_list')
        self.user = User.objects.get(email='johndoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name="Chess Club")
        self.other_club = Club.objects.get(name="The Royal Rooks")
        self.user.select_club(self.club)
        self.member.select_club(self.other_club)

    def test_club_list_url(self):
        self.assertEqual(self.url, '/club_list/')

    def test_get_club_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_get_club_list(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertContains(response, self.club.name)
        self.assertContains(response, self.other_club.name)
