"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase

from clubs.models import User, Club


class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.user.select_club(self.club)

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        self.user.first_name = self.other_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        self.user.last_name = self.other_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        self.user.email = self.other_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        self.user.bio = self.other_user.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_520_characters(self):
        self.user.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user.bio = 'x' * 521
        self._assert_user_is_invalid()

    def test_experience_level_must_not_be_blank(self):
        self.user.experience_level = ''
        self._assert_user_is_invalid()

    def test_experience_level_need_not_be_unique(self):
        self.user.experience_level = self.other_user.experience_level
        self._assert_user_is_valid()

    def test_experience_level_may_contain_520_characters(self):
        self.user.experience_level = 'x' * 520
        self._assert_user_is_valid()

    def test_experience_level_must_not_contain_more_than_520_characters(self):
        self.user.experience_level = 'x' * 521
        self._assert_user_is_invalid()

    def test_personal_statement_must_not_be_blank(self):
        self.user.personal_statement = ''
        self._assert_user_is_invalid()

    def test_personal_statement_need_not_be_unique(self):
        self.user.personal_statement = self.other_user.personal_statement
        self._assert_user_is_valid()

    def test_personal_statement_may_contain_520_characters(self):
        self.user.personal_statement = 'x' * 520
        self._assert_user_is_valid()

    def test_personal_statement_must_not_contain_more_than_520_characters(self):
        self.user.personal_statement = 'x' * 521
        self._assert_user_is_invalid()

    def test_create_user_with_no_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects._create_user(None, 'Password123')

    def test_successful_create_super_user(self):
        user = User.objects.create_superuser(email='super@example.org', password='Password123')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_is_staff_attribute_false_in_superuser(self):
        with self.assertRaises(ValueError):
            user = User.objects.create_superuser(email='super@example.org', password='Password123', is_staff=False)
            self.assertFalse(user.is_staff)
            self.assertTrue(user.is_superuser)

    def test_is_superuser_attribute_false_in_superuser(self):
        with self.assertRaises(ValueError):
            user = User.objects.create_superuser(email='super@example.org', password='Password123', is_superuser=False)
            self.assertTrue(user.is_staff)
            self.assertFalse(user.is_superuser)

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
