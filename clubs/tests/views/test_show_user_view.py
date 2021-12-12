"""Test of the show user view"""

from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class ShowUserTest(TestCase):
    """Test of the show user view"""

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
        self.url = reverse('show_user', kwargs={'user_id': self.member.id})

    def test_show_user_url(self):
        self.assertEqual(self.url,f'/user/{self.member.id}')

    def test_get_show_user_with_user_who_is_member(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'janedoe@example.org')
        self.assertNotContains(response, 'Jamie Doe')
        self.assertNotContains(response, 'jamiedoe@example.org')
        self.assertNotContains(response, 'James Doe')
        self.assertNotContains(response, 'jamesdoe@example.org')
        self.assertNotContains(response, 'Jenny Doe')
        self.assertNotContains(response, 'johndoe@example.org')

    def test_get_show_user_with_user_who_is_officer(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'janedoe@example.org')
        self.assertNotContains(response, 'Jamie Doe')
        self.assertNotContains(response, 'jamiedoe@example.org')
        self.assertNotContains(response, 'James Doe')
        self.assertNotContains(response, 'jamesdoe@example.org')
        self.assertNotContains(response, 'Jenny Doe')
        self.assertNotContains(response, 'johndoe@example.org')

    def test_get_show_user_with_user_who_is_owner(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'janedoe@example.org')
        self.assertNotContains(response, 'Jamie Doe')
        self.assertNotContains(response, 'jamiedoe@example.org')
        self.assertNotContains(response, 'James Doe')
        self.assertNotContains(response, 'jamesdoe@example.org')
        self.assertNotContains(response, 'Jenny Doe')
        self.assertNotContains(response, 'jennydoe@example.org')

    def test_redirects_for_user_that_is_an_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.member.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('start')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_user_with_invalid_id(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.member.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_members_cannot_view_officer(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.officer.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_members_cannot_view_owner(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.owner.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_all_details_are_not_available_for_members(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, self.member.bio, html=True)
        self.assertNotContains(response, '<h6>Bio</h6>', html=True)
        self.assertNotContains(response, self.member.email, html=True)
        self.assertNotContains(response, '<h6>Experience Level</h6>', html=True)
        self.assertNotContains(response, self.member.experience_level, html=True)
        self.assertNotContains(response, '<h6>Personal Statement</h6>', html=True)
        self.assertNotContains(response, self.member.personal_statement, html=True)

    def test_all_details_are_available_for_officers(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, self.member.email, html=True)
        self.assertContains(response, '<h6>Bio</h6>', html=True)
        self.assertContains(response, self.member.bio, html=True)
        self.assertContains(response, '<h6>Experience Level</h6>', html=True)
        self.assertContains(response, self.member.experience_level, html=True)
        self.assertContains(response, '<h6>Personal Statement</h6>', html=True)
        self.assertContains(response, self.member.personal_statement, html=True)

    def test_all_details_are_available_for_owners(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, self.member.email, html=True)
        self.assertContains(response, '<h6>Bio</h6>', html=True)
        self.assertContains(response, self.member.bio, html=True)
        self.assertContains(response, '<h6>Experience Level</h6>', html=True)
        self.assertContains(response, self.member.experience_level, html=True)
        self.assertContains(response, '<h6>Personal Statement</h6>', html=True)
        self.assertContains(response, self.member.personal_statement, html=True)
