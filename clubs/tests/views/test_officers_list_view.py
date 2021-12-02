"""Tests of the officers list view and demotion functionality"""

from django.test import TestCase
from clubs.models import User
from django.urls import reverse

class OfficersListViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.officers_list_url = reverse('officers_list')

    def test_cant_access_officers_list_as_applicant_member_or_officer(self):

        start_url = reverse('start')

        self.client.login( email = self.user.email, password = "Password123" )

        #default role is applicants

        response = self.client.get(self.officers_list_url)

        self.assertRedirects(response, start_url, status_code= 302, target_status_code = 200)

        self.user.role = User.MEMBER
        self.user.save()
        response = self.client.get(self.officers_list_url)
        self.assertRedirects(response, start_url, status_code= 302, target_status_code = 200)

        self.user.role = User.OFFICER
        self.user.save()
        response = self.client.get(self.officers_list_url)
        self.assertRedirects(response, start_url, status_code= 302, target_status_code = 200)


    def test_cant_access_officers_list_logged_out(self):

        response = self.client.get(self.officers_list_url)
        home_url = reverse('home')

        self.assertRedirects(response, home_url, status_code = 302, target_status_code = 200)

    def test_can_access_officers_list_as_owner(self):
        self.user.role = User.OWNER
        self.user.save()

        self.client.login( email = self.user.email, password = "Password123")

        response = self.client.get(self.officers_list_url)

        self.assertEqual( response.status_code, 200)
        self.assertTemplateUsed( response, 'demote_officers.html' )

    def test_succesfully_demote_an_officer(self):
        self.user.role = User.OWNER
        self.user.save()

        officer_to_demote = User.objects.get( email = "janedoe@example.org" )
        officer_to_demote.role = User.OFFICER
        officer_to_demote.save()

        # print( User.objects.get(email = "janedoe@example.org").role == User.OFFICER )

        self.client.login( email = self.user.email, password = "Password123" )

        demote_view_url = reverse('demote_officer', kwargs = {'user_id':officer_to_demote.id} )

        response = self.client.get(demote_view_url)

        self.assertRedirects(response, self.officers_list_url, status_code = 302, target_status_code = 200)

        check_if_demoted = User.objects.get( email = "janedoe@example.org" )

        self.assertEqual( check_if_demoted.role, User.MEMBER )

    def test_cant_demote_an_officer_when_not_logged_in(self):
        officer_to_demote = User.objects.get( email = "janedoe@example.org" )
        officer_to_demote.role = User.OFFICER
        officer_to_demote.save()

        demote_view_url = reverse('demote_officer', kwargs = {'user_id':officer_to_demote.id} )

        response = self.client.get(demote_view_url)

        home_url = reverse('home')

        self.assertRedirects( response, home_url, status_code = 302, target_status_code = 200 )

        check_if_demoted = User.objects.get( email = "janedoe@example.org" )

        self.assertEqual( check_if_demoted.role, User.OFFICER )

    def test_only_officers_show_on_officers_list_page(self):
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

        response = self.client.get( self.officers_list_url )

        users_shown = response.context['officers']

        for user in users_shown:
            self.assertEqual( user.role, User.OFFICER )

    def _create_new_user_with_email(self, email = "somedoe@example.org" ):
        user = User.objects.create_user(
            email = email,
            password = "Password123",
        )
        return user
