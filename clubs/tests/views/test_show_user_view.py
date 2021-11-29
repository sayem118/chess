from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import reverse_with_next

class ShowUserTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.target_user = User.objects.get(email='janedoe@example.org')
        self.target_user.role = User.MEMBER
        self.target_user.save()
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})

    def test_show_user_url(self):
        self.assertEqual(self.url,f'/user/{self.target_user.id}')

    def test_get_show_user_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe@example.org")
        self.assertNotContains(response, "John Doe")
        self.assertNotContains(response, "johndoe@example.org")

    def test_get_show_user_with_invalid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirects_for_user_that_is_not_member(self):
        self.client.login(email=self.target_user.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
