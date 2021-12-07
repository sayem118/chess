"""Tests of the members list view and promotion functionality"""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership


class MembersListViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse('user_list')
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
        self.members_list_url = reverse('members_list')

    def test_cant_access_members_list_as_applicant(self):
        response_url = reverse('start')
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cant_access_members_list_as_member(self):
        response_url = reverse('start')
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cant_access_members_list_as_officer(self):
        response_url = reverse('start')
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cant_access_members_list_logged_out(self):
        response_url = reverse('log_in')

        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        response = self.client.get(self.members_list_url, follow=True)
        self.assertTemplateUsed('log_in.html')

    def test_can_access_members_list_as_owner(self):
        self.client.login(email=self.owner.email, password='Password123')
        self.client.get(self.members_list_url)
        self.assertTemplateUsed('promote_members.html')

    def test_succesfully_promote_a_member(self):
        self.client.login(email=self.owner.email, password='Password123')

        promote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id})
        response = self.client.get(promote_view_url)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_promoted = User.objects.get(email="janedoe@example.org")

        self.assertEqual(check_if_promoted.current_club_role, Membership.OFFICER)
        members_list_url = reverse('members_list')
        self.assertRedirects(response, members_list_url, status_code=302, target_status_code=200)

    def test_cant_promote_a_member_when_not_logged_in(self):
        promote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id})
        response = self.client.get(promote_view_url)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_promoted = User.objects.get(email="janedoe@example.org")

        self.assertEqual(check_if_promoted.current_club_role, Membership.MEMBER)
        home_url = reverse('log_in')
        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

    def test_cant_promote_with_invalid_id(self):
        self.client.login(email=self.owner.email, password="Password123")
        promote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id+9999})
        response = self.client.get(promote_view_url)
        start_url = reverse('start')
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_not_promoted = User.objects.get(email="janedoe@example.org")

        self.assertEqual(check_if_not_promoted.current_club_role, Membership.MEMBER)

    def test_cant_promote_an_owner(self):
        self.client.login(email=self.owner.email, password="Password123")
        promote_view_url = reverse('promote_member', kwargs={'user_id': self.owner.id})
        response = self.client.get(promote_view_url)
        start_url = reverse('members_list')
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_not_promoted = User.objects.get(email="jennydoe@example.org")

        self.assertEqual(check_if_not_promoted.current_club_role, Membership.OWNER)

    def test_cant_promote_an_officer(self):
        self.client.login(email=self.owner.email, password="Password123")
        promote_view_url = reverse('promote_member', kwargs={'user_id': self.officer.id})
        response = self.client.get(promote_view_url)
        start_url = reverse('members_list')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_not_promoted = User.objects.get(email="jamesdoe@example.org")

        self.assertEqual(check_if_not_promoted.current_club_role, Membership.OFFICER)

    def test_cant_promote_an_applicant(self):
        self.client.login(email=self.owner.email, password="Password123")

        promote_view_url = reverse('promote_member', kwargs={'user_id': self.applicant.id})

        response = self.client.get(promote_view_url)

        start_url = reverse('members_list')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_not_promoted = User.objects.get(email="jamiedoe@example.org")

        self.assertEqual(check_if_not_promoted.current_club_role, Membership.APPLICANT)

    def test_cant_promote_a_member_when_not_owner(self):
        self.client.login(email=self.officer.email, password="Password123")
        promote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id})
        response = self.client.get(promote_view_url)
        start_url = reverse('start')
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_not_promoted = User.objects.get(email="janedoe@example.org")

        self.assertEqual(check_if_not_promoted.current_club_role, Membership.MEMBER)

    def test_only_members_show_on_members_list_page(self):
        self.client.login(email=self.owner.email, password='Password123')
        officer = self._create_new_user_with_email("officerdoe@example.org", Membership.OFFICER)

        member = self._create_new_user_with_email("memberdoe@example.org")

        response = self.client.get(self.members_list_url)

        users_shown = response.context['members']

        for user in users_shown:
            self.assertEqual(user.current_club_role, Membership.MEMBER)

    def _create_new_user_with_email(self, email="somedoe@example.org", role=Membership.MEMBER):
        user = User.objects.create_user(
            email=email,
            password="Password123",
        )
        membership = Membership(user=user, club=self.club, role=role)
        membership.save()
        return user
