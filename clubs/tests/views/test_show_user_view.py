from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from clubs.models import User
from clubs.tests.helpers import reverse_with_next

class ShowUserTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.applicant = User.objects.get(email='johndoe@example.org')
        self.officer = User.objects.get(email='janedoe@example.org')
        self.member = User.objects.get(email='jamesdoe@example.org')
        self.owner = User.objects.get(email='jennydoe@example.org')
        self.url = reverse('show_user', kwargs={'user_id': self.member.id})

    def test_show_user_url(self):
        self.assertEqual(self.url,f'/user/{self.member.id}')

    def test_get_show_user_with_user_who_is_member(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "James Doe")
        self.assertContains(response, "jamesdoe@example.org")
        self.assertNotContains(response, "John Doe")
        self.assertNotContains(response, "johndoe@example.org")
        self.assertNotContains(response, "Jane Doe")
        self.assertNotContains(response, "janedoe@example.org")
        self.assertNotContains(response, "Jenny Doe")
        self.assertNotContains(response, "johndoe@example.org")
        self.assertNotContains(response, "<h6>Bio</h6>", html=True)
        self.assertNotContains(response, "<h6>Experience Level</h6>", html=True)
        self.assertNotContains(response, "<h6>Personal Statement</h6>", html=True)

    def test_get_show_user_with_user_who_is_officer(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "James Doe")
        self.assertContains(response, "jamesdoe@example.org")
        self.assertNotContains(response, "John Doe")
        self.assertNotContains(response, "johndoe@example.org")
        self.assertNotContains(response, "Jane Doe")
        self.assertNotContains(response, "janedoe@example.org")
        self.assertNotContains(response, "Jenny Doe")
        self.assertNotContains(response, "johndoe@example.org")
        self.assertContains(response, "<h6>Bio</h6>", html=True)
        self.assertContains(response, "<h6>Experience Level</h6>", html=True)
        self.assertContains(response, "<h6>Personal Statement</h6>", html=True)

    def test_get_show_user_with_user_who_is_owner(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "James Doe")
        self.assertContains(response, "jamesdoe@example.org")
        self.assertNotContains(response, "John Doe")
        self.assertNotContains(response, "johndoe@example.org")
        self.assertNotContains(response, "Jane Doe")
        self.assertNotContains(response, "janedoe@example.org")
        self.assertNotContains(response, "Jenny Doe")
        self.assertNotContains(response, "johndoe@example.org")
        self.assertContains(response, "<h6>Bio</h6>", html=True)
        self.assertContains(response, "<h6>Experience Level</h6>", html=True)
        self.assertContains(response, "<h6>Personal Statement</h6>", html=True)

    def test_redirects_for_user_that_is_an_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.member.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('start')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'start.html')

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_user_with_invalid_id(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.member.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_members_cannot_view_officer(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.officer.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_members_cannot_view_owner(self):
        self.client.login(email=self.member.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.owner.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
