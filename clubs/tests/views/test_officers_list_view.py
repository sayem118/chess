"""Tests of the officers list view and demotion functionality"""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User


class OfficersListViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.officer = User.objects.get(email='janedoe@example.org')
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.officers_list_url = reverse('officers_list')

    def test_cant_access_officers_list_as_applicant_member_or_officer(self):
        start_url = reverse('start')

        self.client.login(email=self.user.email, password="Password123")

        # default role is applicants

        response = self.client.get(self.officers_list_url)

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        #self.user.role = User.MEMBER
        #self.user.save()
        response = self.client.get(self.officers_list_url)
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        #self.user.role = User.OFFICER
        #self.user.save()
        response = self.client.get(self.officers_list_url)
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

    def test_cant_access_officers_list_logged_out(self):
        response = self.client.get(self.officers_list_url)
        home_url = reverse('home')

        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

    def test_can_access_officers_list_as_owner(self):
        self.client.login(email=self.owner.email, password="Password123")

        response = self.client.get(self.officers_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_officers.html')

    def test_successfully_demote_an_officer(self):
        self.client.login(email=self.owner.email, password="Password123")

        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id})

        response = self.client.get(demote_view_url)

        self.assertRedirects(response, self.officers_list_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_demoted = User.objects.get(email="janedoe@example.org")

        #self.assertEqual(check_if_demoted.role, User.MEMBER)

    def test_cant_demote_an_officer_when_not_logged_in(self):
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id})

        response = self.client.get(demote_view_url)

        home_url = reverse('home')

        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_demoted = User.objects.get(email="janedoe@example.org")

        #self.assertEqual(check_if_demoted.role, User.OFFICER)

    def test_cant_demote_an_officer_when_not_owner(self):
        self.client.login(email=self.officer.email, password="Password123")

        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id})

        response = self.client.get(demote_view_url)

        start_url = reverse('start')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="janedoe@example.org")

        #self.assertEqual(check_if_not_demoted.role, User.OFFICER)

    def test_cant_demote_an_member(self):
        self.client.login(email=self.owner.email, password="Password123")

        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.member.id})

        response = self.client.get(demote_view_url)

        home_url = reverse('officers_list')

        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="jamesdoe@example.org")

        #self.assertEqual(check_if_not_demoted.role, User.MEMBER)

    def test_cant_demote_an_applicant(self):
        self.client.login(email=self.owner.email, password="Password123")

        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.user.id})

        response = self.client.get(demote_view_url)

        home_url = reverse('officers_list')

        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="johndoe@example.org")

        #self.assertEqual(check_if_not_demoted.role, User.APPLICANT)

    def test_redirects_for_invalid_id(self):
        self.client.login(email=self.owner.email, password="Password123")

        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id+9999})

        response = self.client.get(demote_view_url)

        home_url = reverse('start')

        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="janedoe@example.org")

        #self.assertEqual(check_if_not_demoted.role, User.OFFICER)

    def test_only_officers_show_on_officers_list_page(self):
        self.client.login(email=self.owner.email, password='Password123')

        response = self.client.get(self.officers_list_url)

        #users_shown = response.context['officers']

        #for user in users_shown:
            #self.assertEqual(user.role, User.OFFICER)

    def _create_new_user_with_email(self, email="somedoe@example.org"):
        user = User.objects.create_user(
            email=email,
            password="Password123",
        )
        return user
