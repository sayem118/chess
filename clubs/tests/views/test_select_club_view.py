"""Test of the select club view"""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership
from clubs.forms import SelectClubForm
from clubs.tests.helpers import reverse_with_next

class SelectClubTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse("select_club")
        self.user = User.objects.get(email='johndoe@example.org')
        self.applicant = User.objects.get(email='jamiedoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.officer = User.objects.get(email="jamesdoe@example.org")
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name="Chess Club")
        self.other_club = Club.objects.get(name="The Royal Rooks")
        membership = Membership(user=self.member, club=self.club, role=Membership.MEMBER)
        membership.save()
        self.user.select_club(self.club)
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)
        self.form_input = {
            'club': self.club
        }

    def test_select_club_url(self):
        self.assertEqual(self.url, '/select_club/')

    def test_redirects_when_not_logged_in(self):
        response_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_successful_get_select_club_with_get(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'select_club.html')
        self.assertEqual(response.status_code, 200)

    """def test_successful_get_select_club_with_post(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.post(self.url, self.form_input)

        form = response.context['form']
        self.assertTrue(isinstance(form, SelectClubForm))
        after_selection = User.objects.get(email="janedoe@example.org")
        print(after_selection.membership_set.all()[1].club)
        self.assertEqual(after_selection.current_club, self.club)

        #self.assertTemplateUsed(response, 'select_club.html')
        #self.assertEqual(response.status_code, 200)"""
