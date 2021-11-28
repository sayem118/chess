"""Tests of the log in view."""
from django.test import TestCase
from django.urls import reverse

from clubs.models import User


class ApproveApplicantViewTestCase(TestCase):
    """Tests of the approve applicant view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.officer = User.objects.get(email="janedoe@example.org")
        self.applicant = User.objects.get(email="johndoe@example.org")
        self.url = reverse("approve_applicant", kwargs={"user_id": self.applicant.id})

    def test_successfully_approve_applicant(self):
        self.assertEqual(self.officer.role, User.OFFICER)
        self.assertEqual(self.applicant.role, User.APPLICANT)
        self.client.login(email=self.officer.email, password="Password123")
        self.client.get(self.url)
        self.applicant = User.objects.get(email="johndoe@example.org")
        self.assertEqual(self.applicant.role, User.MEMBER)

    def test_approve_applicant_redirects_when_not_logged_in(self):
        redirect_url = reverse("home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertEqual(self.applicant.role, User.APPLICANT)

    def test_approve_applicant_redirects_when_not_logged_in_as_officer(self):
        self.officer.role = User.MEMBER
        self.officer.save()
        self.client.login(email=self.officer.email, password="Password123")
        redirect_url = reverse("start")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertEqual(self.applicant.role, User.APPLICANT)
