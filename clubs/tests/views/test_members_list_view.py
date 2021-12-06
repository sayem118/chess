"""Tests of the members list view and promotion functionality"""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User


class MembersListViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.member = User.objects.get(email='jamesdoe@example.org')
        self.officer = User.objects.get(email='janedoe@example.org')
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.members_list_url = reverse('members_list')

    def test_cant_access_members_list_as_applicant_member_or_officer(self):
        response_url = reverse('start')

        # default user role = applicant
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        #self.user.role = User.MEMBER
        #self.user.save()
        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        #self.user.role = User.OFFICER
        #self.user.save()
        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cant_access_members_list_logged_out(self):
        response_url = reverse('home')

        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        response = self.client.get(self.members_list_url, follow=True)
        self.assertTemplateUsed('home.html')

    def test_can_access_members_list_as_owner(self):
        self.client.login(email=self.owner.email, password='Password123')

        self.client.get(self.members_list_url)

        self.assertTemplateUsed('promote_members.html')

    def test_succesfully_promote_a_member(self):
        #self.user.role = User.OWNER
        #self.user.save()

        user_to_promote = User.objects.get(email="janedoe@example.org")
        #user_to_promote.role = User.MEMBER
        #user_to_promote.save()

        self.client.login(email=self.user.email, password='Password123')

        promote_view_url = reverse('promote_member', kwargs={'user_id': user_to_promote.id})

        response = self.client.get(promote_view_url)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_promoted = User.objects.get(email="janedoe@example.org")
        #self.assertEqual(check_if_promoted.role, User.OFFICER)

        members_list_url = reverse('members_list')

        self.assertRedirects(response, members_list_url, status_code=302, target_status_code=200)

    def test_cant_promote_a_member_when_not_logged_in(self):
        user_to_promote = User.objects.get(email="janedoe@example.org")
        #user_to_promote.role = User.MEMBER
        #user_to_promote.save()

        promote_view_url = reverse('promote_member', kwargs={'user_id': user_to_promote.id})

        response = self.client.get(promote_view_url)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.
        check_if_promoted = User.objects.get(email="janedoe@example.org")
        #self.assertEqual(check_if_promoted.role, User.MEMBER)

        home_url = reverse('home')

        self.assertRedirects(response, home_url, status_code=302, target_status_code=200)

    def test_cant_promote_with_invalid_id(self):
        self.client.login(email=self.owner.email, password="Password123")

        promote_view_url = reverse('promote_member', kwargs={'user_id': self.member.id+9999})

        response = self.client.get(promote_view_url)

        start_url = reverse('start')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.

        check_if_not_promoted = User.objects.get(email="jamesdoe@example.org")
        #self.assertEqual(check_if_not_promoted.role, User.MEMBER)

    def test_cant_promote_an_owner(self):
        self.client.login(email=self.owner.email, password="Password123")

        promote_view_url = reverse('promote_member', kwargs={'user_id': self.owner.id})

        response = self.client.get(promote_view_url)

        start_url = reverse('members_list')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.

        check_if_not_promoted = User.objects.get(email="jennydoe@example.org")
        #self.assertEqual(check_if_not_promoted.role, User.OWNER)

    def test_cant_promote_an_officer(self):
        self.client.login(email=self.owner.email, password="Password123")

        promote_view_url = reverse('promote_member', kwargs={'user_id': self.officer.id})

        response = self.client.get(promote_view_url)

        start_url = reverse('members_list')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.

        check_if_not_promoted = User.objects.get(email="janedoe@example.org")
        #self.assertEqual(check_if_not_promoted.role, User.OFFICER)

    def test_cant_promote_an_applicant(self):
        self.client.login(email=self.owner.email, password="Password123")

        promote_view_url = reverse('promote_member', kwargs={'user_id': self.user.id})

        response = self.client.get(promote_view_url)

        start_url = reverse('members_list')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.

        check_if_not_promoted = User.objects.get(email="johndoe@example.org")
        #self.assertEqual(check_if_not_promoted.role, User.APPLICANT)

    def test_cant_promote_a_member_when_not_owner(self):
        #self.user.role = User.OFFICER
        #self.user.save()

        self.client.login(email=self.user.email, password="Password123")

        user_to_promote = User.objects.get(email="janedoe@example.org")
        #user_to_promote.role = User.MEMBER
        #user_to_promote.save()

        promote_view_url = reverse('promote_member', kwargs={'user_id': user_to_promote.id})

        response = self.client.get(promote_view_url)

        start_url = reverse('start')

        self.assertRedirects(response, start_url, status_code=302, target_status_code=200)

        # Getting the user again from the db is needed because the instance user_to_promote points to does not get updated automatically.

        check_if_promoted = User.objects.get(email="janedoe@example.org")
        #self.assertEqual(check_if_promoted.role, User.MEMBER)

    def test_only_members_show_on_members_list_page(self):
        self.client.login(email=self.owner.email, password='Password123')

        # jane doe will be the applicant case

        officer = self._create_new_user_with_email("officerdoe@example.org")
        #officer.role = User.OFFICER
        #officer.save()

        member = self._create_new_user_with_email("memberdoe@example.org")
        #member.role = User.MEMBER
        #member.save()

        response = self.client.get(self.members_list_url)

        #users_shown = response.context['members']

        #for user in users_shown:
            #self.assertEqual(user.role, User.MEMBER)

    def _create_new_user_with_email(self, email="somedoe@example.org"):
        user = User.objects.create_user(
            email=email,
            password="Password123",
        )
        return user
