"""Unit tests for the Membership model."""
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase

from clubs.models import User, Club, Membership


class MembershipModelTestCase(TestCase):
    """Unit tests for the Membership model."""

    fixtures = [
        'clubs/tests/fixtures/users/default_user.json',
        'clubs/tests/fixtures/users/other_users.json',
        'clubs/tests/fixtures/clubs/default_club.json',
        'clubs/tests/fixtures/clubs/other_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name='Chess Club')
        self.other_club = Club.objects.get(name='The Royal Rooks')

    def test_user_cannot_be_blank(self):
        membership = Membership(user=None, club=self.club, role=Membership.OWNER)
        with self.assertRaises(IntegrityError):
            membership.save()

    def test_club_cannot_be_blank(self):
        membership = Membership(user=self.user, club=None, role=Membership.OWNER)
        with self.assertRaises(IntegrityError):
            membership.save()

    def test_role_cannot_be_blank(self):
        membership = Membership(user=self.user, club=self.club, role=None)
        with self.assertRaises(IntegrityError):
            membership.save()

    def test_successful_membership_creation(self):
        membership = Membership(user=self.user, club=self.club, role=Membership.OWNER)
        try:
            membership.save()
        except ValidationError:
            self.fail('Test membership should be valid')
        except IntegrityError:
            self.fail('Test membership should be valid')
        try:
            Membership.objects.get(user=self.user, club=self.club, role=Membership.OWNER)
        except ObjectDoesNotExist:
            self.fail('Test membership should be valid')

    def test_user_cannot_have_more_than_one_role_in_a_club(self):
        membership = Membership(user=self.user, club=self.club, role=Membership.OWNER)
        membership.save()
        fail_membership = Membership(user=self.user, club=self.club, role=Membership.MEMBER)
        with self.assertRaises(IntegrityError):
            fail_membership.save()

    """def test_cannot_have_more_than_one_owner_for_a_club(self):
        membership = Membership(user=self.user, club=self.club, role=Membership.OWNER)
        fail_membership = Membership(user=self.other_user, club=self.club, role=Membership.OWNER)
        with self.assertRaises(IntegrityError):
            fail_membership.save()"""
