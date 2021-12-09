"""Tests of the officers list view and demotion functionality"""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership


class OfficersListViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse('officers_list')
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
        membership = self.club.membership_set.get(user=self.user)
        membership.role = Membership.OWNER
        membership.save()

    def test_officers_list_url(self):
        self.assertEqual(self.url,'/officers_list/')

    def test_cant_access_officers_list_as_applicant(self):
        start_url = reverse('start')
        self.client.login(email=self.applicant.email, password="Password123")
        response = self.client.get(self.url)
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

    def test_cant_access_officers_list_as_member(self):
        start_url = reverse('start')
        self.client.login(email=self.member.email, password="Password123")
        response = self.client.get(self.url)
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

    def test_cant_access_officers_list_as_officer(self):
        start_url = reverse('start')
        self.client.login(email=self.officer.email, password="Password123")
        response = self.client.get(self.url)
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

    def test_cant_access_officers_list_logged_out(self):
        response = self.client.get(self.url)
        home_url = reverse('log_in')
        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

    def test_can_access_officers_list_as_owner(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_officers.html')

    def test_successfully_demote_an_officer(self):
        self.client.login(email=self.owner.email, password="Password123")
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id})
        response = self.client.get(demote_view_url)
        self.assertRedirects(response, self.url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_demoted = User.objects.get(email="jamesdoe@example.org")
        self.assertEqual(check_if_demoted.current_club_role, Membership.MEMBER)

    def test_cant_demote_an_officer_when_not_logged_in(self):
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id})
        response = self.client.get(demote_view_url)
        home_url = reverse('log_in')
        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="jamesdoe@example.org")
        self.assertEqual(check_if_not_demoted.current_club_role, Membership.OFFICER)

    def test_cant_demote_an_officer_when_not_owner(self):
        self.client.login(email=self.officer.email, password="Password123")
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id})
        response = self.client.get(demote_view_url)
        start_url = reverse('start')
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="jamesdoe@example.org")
        self.assertEqual(check_if_not_demoted.current_club_role, Membership.OFFICER)

    def test_cant_demote_an_member(self):
        self.client.login(email=self.owner.email, password="Password123")
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.member.id})
        response = self.client.get(demote_view_url)
        home_url = reverse('officers_list')
        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="janedoe@example.org")
        self.assertEqual(check_if_not_demoted.current_club_role, Membership.MEMBER)

    def test_cant_demote_an_applicant(self):
        self.client.login(email=self.owner.email, password="Password123")
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.applicant.id})
        response = self.client.get(demote_view_url)
        home_url = reverse('officers_list')
        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="jamiedoe@example.org")
        self.assertEqual(check_if_not_demoted.current_club_role, Membership.APPLICANT)

    def test_redirects_for_invalid_id(self):
        self.client.login(email=self.owner.email, password="Password123")
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id+9999})
        response = self.client.get(demote_view_url)
        home_url = reverse('start')
        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance officer_to_demote points to does not get
        # updated automatically.

        check_if_not_demoted = User.objects.get(email="jamesdoe@example.org")
        self.assertEqual(check_if_not_demoted.current_club_role, Membership.OFFICER)

    def test_only_officers_show_on_officers_list_page(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        users_shown = response.context['officers']
        for user in users_shown:
            self.assertEqual(user.current_club_role, Membership.OFFICER)

    def test_redirects_when_no_club_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        demote_view_url = reverse('demote_officer', kwargs={'user_id': self.officer.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('start')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def _create_new_user_with_email(self, email="somedoe@example.org"):
        user = User.objects.create_user(
            email=email,
            password="Password123",
        )
        membership = Membership(user=user, club=self.other_club, role=Membership.OFFICER)
        membership.save()
        return user
