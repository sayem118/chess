"""Test of the user list view"""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from clubs.models import User, Club, Membership


class UserListTest(TestCase, AssertHTMLMixin):
    """Test of the user list view"""

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
        self.officer = User.objects.get(email='jamesdoe@example.org')
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.other_club = Club.objects.get(name='The Royal Rooks')
        self.applicant.select_club(self.other_club)
        self.member.select_club(self.other_club)
        self.officer.select_club(self.other_club)
        self.owner.select_club(self.other_club)

    def test_user_list_url(self):
        self.assertEqual(self.url,'/user_list/')

    def test_get_user_list_when_member(self):
        self.client.login(email=self.member.email, password='Password123')
        self._create_test_users(settings.USERS_PER_PAGE-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        self.assertFalse(response.context['is_paginated'])
        for user_id in range(settings.USERS_PER_PAGE-1):
            self.assertContains(response, f'user{user_id}@test.org')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            user = User.objects.get(email=f'user{user_id}@test.org')
            user_url = reverse('show_user', kwargs={'user_id': user.id})
            self.assertContains(response, user_url)

    def test_get_user_list_with_pagination(self):
        self.client.login(email=self.member.email, password='Password123')
        self._create_test_users(settings.USERS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('user_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('user_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('user_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_that_is_an_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('start')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')

    def test_members_are_displayed_when_logged_in_as_member(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'Jamie Doe')
        self.assertNotContains(response, 'James Doe')
        self.assertNotContains(response, 'John Doe')
        self.assertNotContains(response, 'Jenny Doe')

    def test_user_list_button_in_menu_does_not_display_when_logged_in_as_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        url = reverse('start')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'start.html')
        self.assertNotContains(response, """<a class='nav-link' href='/user_list/'>Users</a>""", html=True)

    def test_user_list_button_in_menu_displays_when_not_logged_in_as_applicant(self):
        self.assert_menu(self.member)
        self.assert_menu(self.officer)
        self.assert_menu(self.owner)

    def test_all_members_are_displayed_when_logged_in_as_officer(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertContains(response, 'James Doe')
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'Jenny Doe')
        self.assertNotContains(response, 'Jamie Doe')
        self.assertNotContains(response, 'John Doe')

    def test_all_members_are_displayed_when_logged_in_as_owner(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertContains(response, 'James Doe')
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'Jenny Doe')
        self.assertNotContains(response, 'Jamie Doe')
        self.assertNotContains(response, 'John Doe')

    def test_redirects_when_no_club_selected(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('start')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def _create_test_users(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
                personal_statement=f'I am {user_id}',
                experience_level='Medium',
            )
            membership = Membership(user=user, club=self.other_club, role=Membership.MEMBER)
            membership.save()

    def assert_menu(self, test_user):
        self.client.login(email=test_user.email, password='Password123')
        url = reverse('start')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'start.html')
        self.assertContains(response, """<a class='nav-link' href='/user_list/'>Users</a>""", html=True)
