"""Test of the select club view"""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next

class SelectClubTest(TestCase):
    """Test of the select club view"""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.other_club = Club.objects.get(name='The Royal Rooks')
        membership = Membership(user=self.member, club=self.club, role=Membership.MEMBER)
        membership.save()
        self.member.select_club(self.club)
        self.member.select_club(self.other_club)
        self.url = reverse('select_club', kwargs={'club_id': self.club.id})

    def test_select_club_url(self):
        self.assertEqual(self.url,f'/select_club/{self.club.id}')

    def test_redirects_when_not_logged_in(self):
        response_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_successful_get_select_club_when_club_selected_with_get(self):
        self.client.login(email=self.member.email, password='Password123')
        response_url = reverse('start')
        current_club_before = self.member.current_club
        response = self.client.get(self.url, follow=True)
        self.member.refresh_from_db()
        current_club_after = self.member.current_club
        self.assertNotEqual(current_club_before, current_club_after)
        self.assertTemplateUsed(response, 'start.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_successful_get_select_club_when_no_club_selected_with_get(self):
        self.client.login(email=self.user.email, password='Password123')
        response_url = reverse('start')
        current_club_before = self.user.current_club
        response = self.client.get(self.url, follow=True)
        self.user.refresh_from_db()
        current_club_after = self.user.current_club
        self.assertNotEqual(current_club_before, current_club_after)
        self.assertTemplateUsed(response, 'start.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_select_club_that_is_already_current_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response_url = reverse('start')
        self.user.select_club(self.club)
        current_club_before = self.user.current_club
        response = self.client.get(self.url, follow=True)
        self.user.refresh_from_db()
        current_club_after = self.user.current_club
        self.assertEqual(current_club_before, current_club_after)
        self.assertTemplateUsed(response, 'start.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cannot_select_a_club_not_member_of(self):
        response_url = reverse('start')
        url = reverse('select_club', kwargs={'club_id': self.other_club.id})
        self.client.login(email=self.user.email, password='Password123')
        current_club_before = self.user.current_club
        response = self.client.get(url, follow=True)
        self.user.refresh_from_db()
        current_club_after = self.user.current_club
        self.assertEqual(current_club_before, current_club_after)
        self.assertTemplateUsed(response, 'start.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cannot_select_club_that_is_invalid(self):
        response_url = reverse('start')
        url = reverse('select_club', kwargs={'club_id': self.club.id+9999})
        self.client.login(email=self.member.email, password='Password123')
        current_club_before = self.member.current_club
        response = self.client.get(url, follow=True)
        self.member.refresh_from_db()
        current_club_after = self.member.current_club
        self.assertEqual(current_club_before, current_club_after)
        self.assertTemplateUsed(response, 'start.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
