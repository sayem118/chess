"""Tests of the create club view."""
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from clubs.forms import CreateClubForm
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class CreateClubViewTestCase(TestCase):
    """Tests of the create club view."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/clubs/default_club.json',
    ]

    def setUp(self):
        self.url = reverse('create_club')
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.form_input = {
            'name': 'Test Club',
            'location': 'Westminster',
            'mission_statement': 'This is a test club'

        }

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/')

    def test_get_create_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertFalse(form.is_bound)

    def test_get_create_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_create_club_redirects_when_not_logged_in(self):
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
        self.assertNotEqual(club.mission_statement, 'This is a test club')
