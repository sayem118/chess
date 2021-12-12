"""Test of the apply for club view"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class ApplyForClubTest(TestCase):
    """Test of the apply for club view"""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/clubs/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.url = reverse('apply', kwargs={'club_id': self.club.id})

    def test_apply_url(self):
        self.assertEqual(self.url,f'/apply/{self.club.id}')

    def test_successful_apply_for_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response_url = reverse('my_clubs')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.user.refresh_from_db()
        try:
            self.assertEqual(self.user.membership_set.get(club=self.club).role, Membership.APPLICANT)
        except ObjectDoesNotExist:
            self.fail('User should be an applicant')

    def test_member_of_club_cannot_apply_for_the_same_club(self):
        membership = Membership(user=self.user, club=self.club, role=Membership.OWNER)
        membership.save()
        self.client.login(email=self.user.email, password='Password123')
        response_url = reverse('my_clubs')
        with self.assertRaises(IntegrityError):
            response = self.client.get(self.url, follow=True)
            self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
            self.user.refresh_from_db()
            try:
                self.assertEqual(self.user.membership_set.get(club=self.club).role, Membership.OWNER)
            except ObjectDoesNotExist:
                self.fail('User should be an owner')

    def test_cannot_apply_for_a_club_that_does_not_exist(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('apply', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('my_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_apply_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
