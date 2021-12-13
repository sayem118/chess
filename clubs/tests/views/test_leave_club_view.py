"""Test of the leave club view"""

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class LeaveClubTest(TestCase):
    """Test of the leave club view"""

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
        self.member.select_club(self.other_club)
        self.url = reverse('leave_club', kwargs={'club_id': self.other_club.id})

    def test_leave_club_url(self):
        self.assertEqual(self.url,f'/leave_club/{self.other_club.id}')

    def test_successful_leave_club(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        club_after_member_leave = Club.objects.get(name='The Royal Rooks')
        with self.assertRaises(ObjectDoesNotExist):
            club_after_member_leave.membership_set.get(user=self.member)

    def test_cannot_leave_a_club_that_does_not_exist(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('apply', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cannot_leave_club_user_is_not_in(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.other_club.refresh_from_db()
        with self.assertRaises(ObjectDoesNotExist):
            self.other_club.membership_set.get(user=self.user)

    def test_user_leaves_current_club(self):
        self.club.add_user(self.member)
        self.member.select_club(self.club)
        self.url = reverse('leave_club', kwargs={'club_id': self.club.id})
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.club.refresh_from_db()
        self.member.refresh_from_db()
        self.assertTrue(self.member.current_club, self.other_club)
        try:
            self.other_club.membership_set.get(user=self.member)
        except ObjectDoesNotExist:
            self.fail('User should be in Chess Club')
        with self.assertRaises(ObjectDoesNotExist):
            self.club.membership_set.get(user=self.member)

    def test_user_leaves_club_which_is_not_current(self):
        self.club.add_user(self.member)
        self.member.select_club(self.club)
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.other_club.refresh_from_db()
        self.member.refresh_from_db()
        self.assertTrue(self.member.current_club, self.club)
        try:
            self.club.membership_set.get(user=self.member)
        except ObjectDoesNotExist:
            self.fail('User should be in Chess Club')
        with self.assertRaises(ObjectDoesNotExist):
            self.other_club.membership_set.get(user=self.member)

    def test_user_cannot_leave_club_if_owner(self):
        self.user.select_club(self.club)
        self.url = reverse('leave_club', kwargs={'club_id': self.club.id})
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.club.refresh_from_db()
        try:
            self.club.membership_set.get(user=self.user)
        except ObjectDoesNotExist:
            self.fail('User should be in Chess Club')

    def test_get_apply_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
