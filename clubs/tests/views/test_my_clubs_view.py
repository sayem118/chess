"""Test of the my clubs view"""

from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin

from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class MyClubsTest(TestCase,AssertHTMLMixin):

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse('my_clubs')
        self.member = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Chess Club")
        self.other_club = Club.objects.get(name="The Royal Rooks")
        self.member.select_club(self.other_club)

    def test_my_clubs_url(self):
        self.assertEqual(self.url, '/my_clubs/')

    def test_get_my_clubs_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_get_my_clubs(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        self.assertContains(response, self.club)
        self.assertContains(response, self.other_club)
