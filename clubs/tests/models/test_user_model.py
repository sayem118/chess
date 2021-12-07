"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase

from clubs.models import User, Club, Membership


class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json',
        'clubs/tests/fixtures/memberships/memberships.json'
    ]

    def setUp(self):
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

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(email="janedoe@example.org")
        self.user.first_name = second_user.first_name
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
        second_user = User.objects.get(email="janedoe@example.org")
        self.user.last_name = second_user.last_name
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
        second_user = User.objects.get(email="janedoe@example.org")
        self.user.email = second_user.email
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
        second_user = User.objects.get(email="janedoe@example.org")
        self.user.bio = second_user.bio
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
        second_user = User.objects.get(email="janedoe@example.org")
        self.user.experience_level = second_user.experience_level
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
        second_user = User.objects.get(email="janedoe@example.org")
        self.user.personal_statement = second_user.personal_statement
        self._assert_user_is_valid()

    def test_personal_statement_may_contain_520_characters(self):
        self.user.personal_statement = 'x' * 520
        self._assert_user_is_valid()

    def test_personal_statement_must_not_contain_more_than_520_characters(self):
        self.user.personal_statement = 'x' * 521
        self._assert_user_is_invalid()

    def test_create_user_with_no_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects._create_user(None, "Password123")

    def test_successful_create_super_user(self):
        user = User.objects.create_superuser(email="super@example.org", password="Password123")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_is_staff_attribute_false_in_superuser(self):
        with self.assertRaises(ValueError):
            user = User.objects.create_superuser(email="super@example.org", password="Password123", is_staff=False)
            self.assertFalse(user.is_staff)
            self.assertTrue(user.is_superuser)

    def test_is_superuser_attribute_false_in_superuser(self):
        with self.assertRaises(ValueError):
            user = User.objects.create_superuser(email="super@example.org", password="Password123", is_superuser=False)
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
