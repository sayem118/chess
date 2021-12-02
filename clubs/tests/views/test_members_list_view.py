"""Tests of the members list view and promotion functionality"""

from django.test import TestCase
from clubs.models import User,UserManager
from django.urls import reverse

class MembersListViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.members_list_url = reverse('members_list')

    def test_cant_access_members_list_as_applicant_member_or_officer(self):
        response_url = reverse('start')

        # default user role = applicant
        self.client.login( email = self.user.email, password = 'Password123' )
        response = self.client.get(self.members_list_url)
        self.assertRedirects( response, response_url, status_code = 302,target_status_code = 200 )

        self.user.role = User.MEMBER
        self.user.save()
        response = self.client.get(self.members_list_url)
        self.assertRedirects( response, response_url, status_code = 302,target_status_code = 200 )

        self.user.role = User.OFFICER
        self.user.save()
        response = self.client.get(self.members_list_url)
        self.assertRedirects( response, response_url, status_code = 302,target_status_code = 200 )

    def test_cant_access_members_list_logged_out(self):
        response_url = reverse('home')

        response = self.client.get(self.members_list_url)
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)

        response = self.client.get(self.members_list_url, follow = True)
        self.assertTemplateUsed('home.html')

    def test_can_access_members_list_as_owner(self):
        self.user.role = User.OWNER
        self.user.save()

        self.client.login( email = self.user.email, password = 'Password123' )

        self.client.get(self.members_list_url)

        self.assertTemplateUsed('promote_members.html')

    def test_succesfully_promote_a_member(self):
        self.user.role = User.OWNER
        self.user.save()

        user_to_promote = User.objects.get( email = "janedoe@example.org" )
        user_to_promote.role = User.MEMBER
        user_to_promote.save()

        self.client.login( email = self.user.email, password = 'Password123')

        promote_view_url = reverse('promote_member', kwargs = {'user_id':user_to_promote.id} )

        response = self.client.get( promote_view_url )

        user_to_promote = User.objects.get( email = "janedoe@example.org" )
        self.assertEqual(user_to_promote.role , User.OFFICER)

        members_list_url = reverse('members_list')

        self.assertRedirects( response, members_list_url, status_code = 302, target_status_code = 200 )


    def test_cant_promote_a_member_when_not_logged_in(self):
        user_to_promote = User.objects.get( email = "janedoe@example.org" )
        user_to_promote.role = User.MEMBER
        user_to_promote.save()

        promote_view_url = reverse('promote_member', kwargs = {'user_id':user_to_promote.id} )

        response = self.client.get( promote_view_url )

        user_to_promote = User.objects.get( email = "janedoe@example.org" )
        self.assertEqual(user_to_promote.role , User.MEMBER)

        home_url = reverse('home')

        self.assertRedirects( response, home_url, status_code = 302, target_status_code = 200 )

    def test_only_members_show_on_members_list_page(self):
        self.user.role = User.OWNER
        self.user.save()
        self.client.login( email = self.user.email, password = 'Password123' )

        # jane doe will be the applicant case

        officer = self._create_new_user_with_email("officerdoe@example.org")
        officer.role = User.OFFICER
        officer.save()

        member = self._create_new_user_with_email("memberdoe@example.org")
        member.role = User.MEMBER
        member.save()

        response = self.client.get( self.members_list_url )

        users_shown = response.context['members']

        for user in users_shown:
            self.assertEqual( user.role, User.MEMBER )

    def _create_new_user_with_email(self, email = "somedoe@example.org" ):
        user = User.objects.create_user(
            email = email,
            password = "Password123",
        )
        return user
