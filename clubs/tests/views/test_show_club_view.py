"""Test of the show club view"""

from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class ShowClubTest(TestCase):
    """Test of the show club view"""

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
        self.user.select_club(self.club)
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        self.url = reverse('show_club', kwargs={'club_id': self.club.id})

    def test_show_club_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}')

    def test_get_show_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_club_with_invalid_id(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_club', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('start')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')

    def test_get_successful_show_club(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_club', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_is_accessible_to_all_roles(self):
        self.assert_accessible(self.applicant)
        self.assert_accessible(self.member)
        self.assert_accessible(self.officer)
        self.assert_accessible(self.owner)

    def test_is_accessable_with_no_club_selected(self):
        self.assert_accessible(self.user)

    def test_is_accessable_for_user_who_is_not_in_any_club(self):
        User.objects.create_user(email='test@example.org', password='Password123')
        test_user = User.objects.get(email='test@example.org')
        self.assert_accessible(test_user)

    def assert_accessible(self, test_user):
        self.client.login(email=test_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertContains(response, self.club.name)
        self.assertContains(response, self.club.owner.full_name)
        self.assertContains(response, self.club.location)
        self.assertContains(response, self.club.mission_statement)
