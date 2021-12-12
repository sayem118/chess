"""Test of the transfer ownership view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership


class TransferOwnershipTest(TestCase):
    """Test of the transfer ownership view"""

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
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        membership = Membership.objects.get(user=self.user, club=self.club)
        membership.role = Membership.OWNER
        membership.save()
        self.url = reverse('transfer_ownership', kwargs={'user_id': self.officer.id})

    def test_transfer_ownership_url(self):
        self.assertEqual(self.url,f'/transfer_ownership/{self.officer.id}')

    def test_successfully_transfer_ownership(self):
        self.client.login(email=self.owner.email, password='Password123')
        redirect_url = reverse('start')
        response = self.client.get(self.url, follow=True)
        self.owner.refresh_from_db()
        self.officer.refresh_from_db()
        self.assertEqual(self.officer.current_club_role, Membership.OWNER)
        self.assertEqual(self.owner.current_club_role, Membership.OFFICER)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_cannot_transfer_ownership_to_member(self):
        self.client.login(email=self.owner.email, password='Password123')
        redirect_url = reverse('start')
        url = reverse('transfer_ownership', kwargs={'user_id': self.member.id})
        response = self.client.get(url, follow=True)
        self.owner.refresh_from_db()
        self.member.refresh_from_db()
        self.assertEqual(self.owner.current_club_role, Membership.OWNER)
        self.assertEqual(self.member.current_club_role, Membership.MEMBER)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_cannot_transfer_ownership_to_applicant(self):
        self.client.login(email=self.owner.email, password='Password123')
        redirect_url = reverse('start')
        url = reverse('transfer_ownership', kwargs={'user_id': self.applicant.id})
        response = self.client.get(url, follow=True)
        self.owner.refresh_from_db()
        self.applicant.refresh_from_db()
        self.assertEqual(self.owner.current_club_role, Membership.OWNER)
        self.assertEqual(self.applicant.current_club_role, Membership.APPLICANT)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_that_is_a_not_owner(self):
        self.assert_redirects(self.applicant)
        self.assert_redirects(self.member)
        self.assert_redirects(self.officer)

    def test_redirects_for_user_that_is_invalid(self):
        self.client.login(email=self.owner.email, password='Password123')
        response_url = reverse('start')
        url = reverse('transfer_ownership', kwargs={'user_id': self.officer.id+9999})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_transfer_ownership_redirects_when_not_logged_in(self):
        response_url = reverse('log_in')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_who_is_not_in_any_club(self):
        User.objects.create_user(email='test@example.org', password='Password123')
        test_user = User.objects.get(email='test@example.org')
        self.assert_redirects(test_user)

    def test_redirects_when_no_club_selected(self):
        self.assert_redirects(self.user)

    def assert_redirects(self, test_user):
        self.client.login(email=test_user.email, password='Password123')
        response_url = reverse('start')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
