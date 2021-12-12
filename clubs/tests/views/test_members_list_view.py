"""Tests of the members list view and promotion functionality"""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User, Club, Membership


class MembersListViewTestCase(TestCase):
    """Tests of the members list view and promotion functionality"""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
        self.url = reverse('members_list')
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

    def test_cannot_access_members_list_when_not_owner(self):
        self.assert_redirects(self.applicant)
        self.assert_redirects(self.member)
        self.assert_redirects(self.officer)

    def test_member_list_redirects_when_not_logged_in(self):
        response_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed('log_in.html')

    def test_can_access_members_list_as_owner(self):
        self.client.login(email=self.owner.email, password='Password123')
        self.client.get(self.url)
        self.assertTemplateUsed('promote_members.html')

    def test_succesfully_promote_a_member(self):
        self.client.login(email=self.owner.email, password='Password123')

        promote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id})
        response = self.client.get(promote_view_url)
        url = reverse('members_list')
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        self.check_user_role(self.member, Membership.OFFICER)

    def test_cannot_promote_a_member_when_not_logged_in(self):
        response = self.client.get(self.url)
        home_url = reverse('log_in')
        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)
        self.check_user_role(self.member)

    def test_cannot_promote_with_invalid_id(self):
        self.client.login(email=self.owner.email, password='Password123')
        promote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id+9999})
        response = self.client.get(promote_view_url)
        start_url = reverse('start')
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)
        self.check_user_role(self.member)

    def test_cannot_promote_user_who_is_not_member(self):
        self.assert_cannot_promote_role(self.applicant, Membership.APPLICANT)
        self.assert_cannot_promote_role(self.officer, Membership.OFFICER)
        self.assert_cannot_promote_role(self.owner, Membership.OWNER, 'members_list')

    def test_cannot_promote_a_member_when_not_owner(self):
        self.assert_redirects(self.applicant)
        self.assert_redirects(self.member)
        self.assert_redirects(self.officer)
        self.check_user_role(self.member)

    def test_only_members_show_on_members_list_page(self):
        self.client.login(email=self.owner.email, password='Password123')
        officer = self._create_new_user_with_email('officerdoe@example.org', Membership.OFFICER)
        member = self._create_new_user_with_email('memberdoe@example.org')
        response = self.client.get(self.url)
        users_shown = response.context['members']

        for user in users_shown:
            self.assertEqual(user.current_club_role, Membership.MEMBER)

    def test_redirects_when_no_club_selected(self):
        self.assert_redirects(self.user)

    def _create_new_user_with_email(self, email='somedoe@example.org', role=Membership.MEMBER):
        user = User.objects.create_user(
            email=email,
            password='Password123',
        )
        membership = Membership(user=user, club=self.club, role=role)
        membership.save()
        return user

    def assert_redirects(self, test_user):
        if test_user:
            self.client.login(email=test_user.email, password='Password123')
        demote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id})
        response = self.client.get(demote_view_url)
        start_url = reverse('start')
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

    def assert_cannot_promote_role(self, test_user, role, url='start'):
        self.client.login(email=test_user.email, password='Password123')
        promote_view_url = reverse('promote_member', kwargs={'user_id': test_user.id})
        response = self.client.get(promote_view_url)
        start_url = reverse(url)
        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)
        self.check_user_role(test_user, role)

    def check_user_role(self, test_user, role=Membership.MEMBER):
        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        test_user.refresh_from_db()
        self.assertEqual(test_user.current_club_role, role)
