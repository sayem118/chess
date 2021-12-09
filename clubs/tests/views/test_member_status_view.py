"""Test of the member status view"""

from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from clubs.models import User, Club, Membership


class MemberStatusTest(TestCase, AssertHTMLMixin):

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse('member_status')
        self.user = User.objects.get(email='johndoe@example.org')
        self.applicant = User.objects.get(email='jamiedoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.officer = User.objects.get(email="jamesdoe@example.org")
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name="Chess Club")
        self.other_club = Club.objects.get(name="The Royal Rooks")
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        membership = Membership(user=self.officer, club=self.club, role=Membership.APPLICANT)
        membership.save()
        test_club = Club(name="Test Club", location="Brighton", mission_statement="Test")
        test_club.save()
        other_membership = Membership(user=self.officer, club=test_club, role=Membership.OWNER)
        other_membership.save()

    def test_member_status_url(self):
        self.assertEqual(self.url,'/member_status/')

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_get_member_status(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_status.html')
        self.assertContains(response, self.other_club.name, html=True)
        self.assertContains(response, "Member", html=True)
        self.assertContains(response, """<a class="nav-link" href="/member_status/">Member status</a>""", html=True)

    def test_user_with_no_club_redirects_to_start(self):
        test_user = User.objects.create_user(email='test@example.org', password='Password123')
        self.client.login(email=test_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('start')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')
        self.assertNotContains(response, """<a class="nav-link" href="/member_status/">Member status</a>""", html=True)

    def test_user_who_is_apart_of_multiple_clubs_displays_all_clubs(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_status.html')
        self.assertContains(response, """<a class="nav-link" href="/member_status/">Member status</a>""", html=True)
        self.assertContains(response, self.club.name, html=True)
        self.assertContains(response, "Applicant", html=True)
        self.assertContains(response, self.other_club.name, html=True)
        self.assertContains(response, "Officer", html=True)
        self.assertContains(response, "Test Club", html=True)
        self.assertContains(response, "Owner", html=True)
