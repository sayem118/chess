"""Test of the transfer ownership view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership


class TransferOwnershipTest(TestCase):

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
        self.officer = User.objects.get(email="jamesdoe@example.org")
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name="Chess Club")
        self.other_club = Club.objects.get(name="The Royal Rooks")
        self.user.select_club(self.club)
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        self.url = reverse("transfer_ownership", kwargs={"user_id": self.officer.id})

    def test_successfully_transfer_ownership(self):
        self.client.login(email=self.owner.email, password="Password123")
        redirect_url = reverse("start")
        response = self.client.get(self.url, follow=True)
        owner_to_check = User.objects.get(email="jamesdoe@example.org")
        officer_to_check = User.objects.get(email="jennydoe@example.org")
        self.assertEqual(owner_to_check.current_club_role, Membership.OWNER)
        self.assertEqual(officer_to_check.current_club_role, Membership.OFFICER)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_cannot_transfer_ownership_to_member(self):
        self.client.login(email=self.owner.email, password="Password123")
        redirect_url = reverse("start")
        url = reverse("transfer_ownership", kwargs={"user_id": self.member.id})
        response = self.client.get(url, follow=True)
        owner_to_check = User.objects.get(email="jennydoe@example.org")
        officer_to_check = User.objects.get(email="jamesdoe@example.org")
        self.assertEqual(owner_to_check.current_club_role, Membership.OWNER)
        self.assertEqual(officer_to_check.current_club_role, Membership.OFFICER)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_cannot_transfer_ownership_to_applicant(self):
        self.client.login(email=self.owner.email, password="Password123")
        redirect_url = reverse("start")
        url = reverse("transfer_ownership", kwargs={"user_id": self.applicant.id})
        response = self.client.get(url, follow=True)
        owner_to_check = User.objects.get(email="jennydoe@example.org")
        officer_to_check = User.objects.get(email="jamesdoe@example.org")
        self.assertEqual(owner_to_check.current_club_role, Membership.OWNER)
        self.assertEqual(officer_to_check.current_club_role, Membership.OFFICER)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_that_is_an_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        response_url = reverse('start')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_that_is_a_member(self):
        self.client.login(email=self.member.email, password='Password123')
        response_url = reverse('start')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_that_is_a_officer(self):
        self.client.login(email=self.officer.email, password='Password123')
        response_url = reverse('start')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_id_that_is_invalid(self):
        self.client.login(email=self.owner.email, password='Password123')
        response_url = reverse('start')
        url = reverse("transfer_ownership", kwargs={"user_id": self.officer.id+9999})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
