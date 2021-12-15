"""Tests of the create tournament view."""
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from clubs.forms import CreateTournamentForm
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class CreateTournamentViewTestCase(TestCase):
    """Tests of the create tournament view."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse('create_tournament')
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

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_tournament/')

    def test_get_create_tournament(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tournament.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTournamentForm))
        self.assertFalse(form.is_bound)

    def test_get_create_tournamenet_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    """def test_post_create_tournament_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_create_club_if_apart_of_no_other_clubs(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        club_to_check = Club.objects.get(name='Test Club')
        self.assertEqual(club_to_check.location, 'Westminster')
        self.assertEqual(club_to_check.mission_statement, 'This is a test club')
        try:
            membership_of_owner = club_to_check.membership_set.get(role=Membership.OWNER)
            self.assertTrue(membership_of_owner.user, self.user)
        except ObjectDoesNotExist:
            self.fail('The owner of the club should be the user that created it')

    def test_successful_create_club_if_apart_of_other_clubs(self):
        membership = Membership(user=self.user, club=self.club, role=Membership.OWNER)
        membership.save()
        self.user.select_club(self.club)
        self.client.login(email=self.user.email, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        club_to_check = Club.objects.get(name='Test Club')
        self.assertEqual(club_to_check.location, 'Westminster')
        self.assertEqual(club_to_check.mission_statement, 'This is a test club')
        try:
            membership_of_owner = club_to_check.membership_set.get(role=Membership.OWNER)
            self.assertTrue(membership_of_owner.user, self.user)
        except ObjectDoesNotExist:
            self.fail('The owner of the club should be the user that created it')

    def test_cannot_create_a_club_with_same_name(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['name'] = 'Chess Club'
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('my_clubs')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        club = Club.objects.get(name='Chess Club')
        self.assertNotEqual(club.location, 'Westminster')
        self.assertNotEqual(club.mission_statement, 'This is a test club')"""
