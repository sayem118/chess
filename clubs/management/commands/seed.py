from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker

from clubs.models import User, Club, Membership


class Command(BaseCommand):
    USER_COUNT = 100
    CLUB_COUNT = 3
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        example_clubs = self.create_clubs()
        example_users = self.create_users()
        self.add_example_users_to_default_club(example_users)
        self.add_default_users_to_example_clubs(example_clubs)

    def create_users(self):
        self.create_default_users()
        user_count = 1
        users = []
        while user_count <= self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            try:
                users.append(self.create_user())
            except IntegrityError:
                continue
            user_count += 1
        print("User seeding complete.      ")
        return users

    def create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self.create_email(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        experience_level = self.faker.text(max_nb_chars=520)
        personal_statement = self.faker.text(max_nb_chars=520)
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.DEFAULT_PASSWORD,
            bio=bio,
            experience_level=experience_level,
            personal_statement=personal_statement
        )
        return user

    def create_clubs(self):
        self.create_default_club()
        club_count = 1
        clubs = []
        while club_count <= self.CLUB_COUNT:
            print(f"Seeding club {club_count}/{self.USER_COUNT}", end='\r')
            try:
                clubs.append(self.create_club())
            except IntegrityError:
                continue
            club_count += 1
        print("Club seeding complete.      ")
        return clubs

    def create_club(self):
        name = self.faker.word()
        location = self.faker.city()
        mission_statement = self.faker.text(max_nb_chars=520)
        club = Club.objects.create(
            name=name,
            location=location,
            mission_statement=mission_statement
        )
        return club

    def create_email(self, first_name, last_name):
        email = f'{first_name.lower()}.{last_name.lower()}@example.org'
        return email

    def create_default_users(self):
        """Creates the default users"""

        User.objects.create_user(
            email='jeb@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Jebediah',
            last_name='Kerman',
        )

        User.objects.create_user(
            email='val@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Valentina',
            last_name='Kerman',
        )

        User.objects.create_user(
            email='billie@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Billie',
            last_name='Kerman',
        )

    def create_default_club(self):
        """Creates the default clubs"""

        Club.objects.create(
            name='Kerbal Chess Club',
            location='London',
            mission_statement='How much wood would a woodchuck chuck if a woodchuck could chuck wood.'
        )

    def add_example_users_to_default_club(self, users):
        default_club = Club.objects.get(name='Kerbal Chess Club')

        for i in range(len(users)):
            user = users[i]
            default_club.add_user(user)

            if i == len(users) - 1:
                default_club.change_role(user, Membership.OWNER)
            elif i > 2 * len(users) // 3:
                default_club.change_role(user, Membership.OFFICER)
            elif i > len(users) // 3:
                default_club.change_role(user, Membership.MEMBER)

    def add_default_users_to_example_clubs(self, clubs):
        user1 = User.objects.get(email='jeb@example.org')
        club1 = clubs[0]
        club1.add_user(user1)
        club1.change_role(user1, Membership.OFFICER)

        user2 = User.objects.get(email='val@example.org')
        club2 = clubs[1]
        club2.add_user(user2)
        club2.change_role(user2, Membership.OWNER)

        user3 = User.objects.get(email='billie@example.org')
        club3 = clubs[2]
        club3.add_user(user3)
        club3.change_role(user3, Membership.MEMBER)
