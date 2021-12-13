"""Unit tests for the Club model."""
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase

from clubs.models import User, Club, Membership


class ClubModelTestCase(TestCase):
    """Unit tests for the Club model."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.other_club = Club.objects.get(name='The Royal Rooks')

    def test_valid_club(self):
        self._assert_club_is_valid()

    def test_name_must_not_be_blank(self):
        self.club.name = ''
        self._assert_club_is_invalid()

    def test_name_must_be_unique(self):
        self.club.name = self.other_club.name
        self._assert_club_is_invalid()

    def test_name_may_contain_50_characters(self):
        self.club.name = 'x' * 50
        self._assert_club_is_valid()

    def test_name_must_not_contain_more_than_50_characters(self):
        self.club.name = 'x' * 51
        self._assert_club_is_invalid()

    def test_location_must_not_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()

    def test_location_may_not_be_unique(self):
        self.club.location = self.other_club.location
        self._assert_club_is_valid()

    def test_location_may_contain_50_characters(self):
        self.club.location = 'x' * 50
        self._assert_club_is_valid()

    def test_location_must_not_contain_more_than_50_characters(self):
        self.club.location = 'x' * 51
        self._assert_club_is_invalid()

    def test_mission_statement_may_be_blank(self):
        self.club.mission_statement = ''
        self._assert_club_is_valid()

    def test_mission_statement_may_not_be_unique(self):
        self.club.mission_statement = self.other_club.mission_statement
        self._assert_club_is_valid()

    def test_mission_statement_may_contain_520_characters(self):
        self.club.mission_statement = 'x' * 520
        self._assert_club_is_valid()

    def test_mission_statement_must_not_contain_more_than_520_characters(self):
        self.club.mission_statement = 'x' * 521
        self._assert_club_is_invalid()

    def test_create_club_with_no_name_raises_error(self):
        with self.assertRaises(IntegrityError):
            Club(name=None, location='London', mission_statement='To play chess').save()

    def test_create_club_with_no_location_raises_error(self):
        with self.assertRaises(IntegrityError):
            Club(name='Chess', location=None, mission_statement='To play chess').save()

    def test_successful_create_club(self):
        club = Club(name='Chess', location='London', mission_statement='To play chess')
        club.save()
        self.assertEqual(Club.objects.get(name=club.name), club)

    def test_successful_add_user_to_club(self):
        self.club.add_user(self.user)
        self.assertEqual(self.club.associates.get(email=self.user.email), self.user)

    def test_user_in_club_exists(self):
        self.club.add_user(self.user)
        self.assertTrue(self.club.exist(user=self.user))

    def test_user_role_is_confirmed_correctly(self):
        self.club.add_user(self.user)
        self.assertTrue(self.club.is_of_role(self.user, Membership.APPLICANT))

    def test_incorrect_user_role_returns_false(self):
        self.club.add_user(self.user)
        self.assertFalse(self.club.is_of_role(self.user, Membership.MEMBER))

    def test_user_role_is_changed_correctly(self):
        self.club.add_user(self.user)
        self.club.change_role(self.user, Membership.MEMBER)
        self.assertTrue(self.club.is_of_role(self.user, Membership.MEMBER))

    def test_cannot_change_role_for_user_not_in_club(self):
        self.other_club.change_role(self.user, Membership.MEMBER)
        check_club_has_not_changed = Club.objects.get(name='The Royal Rooks')
        with self.assertRaises(ObjectDoesNotExist):
            check_club_has_not_changed.membership_set.get(user=self.user)

    def test_club_owner_is_correct(self):
        membership = Membership(user=self.user, club=self.club, role=Membership.OWNER)
        membership.save()
        self.user.select_club(self.club)
        self.assertEqual(self.club.owner, self.user)

    def test_club_owner_property_raises_error_when_no_owner(self):
        self.assertEqual(self.club.owner, None)

    def test_str_returns_club_name(self):
        self.assertEqual(self.club.__str__(), self.club.name)

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()
