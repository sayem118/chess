"""Tests of the approve applicant view."""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership


class ApproveApplicantViewTestCase(TestCase):
    """Tests of the approve applicant view."""

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
        self.url = reverse('approve_applicant', kwargs={'user_id': self.applicant.id})

    def test_approve_applicant_not_url(self):
        self.assertEqual(self.url, f'/approve_applicant/{self.applicant.id}')

    def test_successfully_approve_applicant(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get(self.url)
        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.current_club_role, Membership.MEMBER)

    def test_approve_applicant_not_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_approve_applicant_not_redirects_when_not_logged_in_as_officer(self):
        self.assert_redirects(self.applicant, Membership.APPLICANT)
        self.assert_redirects(self.member, Membership.MEMBER)

    def test_redirects_when_no_club_selected(self):
        self.assert_redirects(self.user)

    def test_cannot_approve_member(self):
        self.client.login(email=self.officer.email, password='Password123')
        redirect_url = reverse('applicants_list')
        url = reverse('approve_applicant', kwargs={'user_id': self.member.id})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertEqual(self.applicant.current_club_role, Membership.APPLICANT)
        self.assertEqual(self.member.current_club_role, Membership.MEMBER)

    def test_redirects_with_invalid_applicant_not_id(self):
        self.client.login(email=self.officer.email, password='Password123')
        url = reverse('approve_applicant', kwargs={'user_id': self.applicant.id + 9999})
        redirect_url = reverse('start')
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def assert_redirects(self, test_user, role=None):
        self.client.login(email=test_user.email, password='Password123')
        response_url = reverse('start')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        if role is not None:
            self.assertEqual(test_user.current_club_role, role)
