from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from faker import Faker
from clubs.models import User
from random import choices

class Command(BaseCommand):
    USER_COUNT = 100
    POST_COUNT = 2000
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    """ Setting probabilities for the every users role """
    ROLES = [0, 1, 2, 3]
    ROLES_PROBABILITES = [0.5, 0.3, 0.28, 0.02]
    ROLES_NAMES = ['APPLICANT', 'MEMBER', 'OFFICER', 'OWNER']
    ROLES_DICT = dict(zip(ROLES_NAMES, ROLES))    

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()

    def create_users(self):
        self.create_default_users()
        user_count = 1
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            try:
                self.create_user()
            except:
                continue
            user_count += 1
        print("User seeding complete.      ")

    def create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self.create_email(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        experience_level = self.faker.text(max_nb_chars=520)
        personal_statement = self.faker.text(max_nb_chars=520)
        role = self.generate_random_role()
        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.DEFAULT_PASSWORD,
            bio=bio,
            experience_level=experience_level,
            personal_statement=personal_statement,
            role = role 
        )


    def generate_random_role(self):
        result = choices(self.ROLES, self. ROLES_PROBABILITES)
        return result[0] 

    def create_email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def create_default_users(self):
        """Creates the default users"""
        User.objects.create_user(
            email='jeb@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Jebediah',
            last_name='Kerman',
            role = self.ROLES_DICT['MEMBER']
        )

        User.objects.create_user(
            email='val@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Valentina',
            last_name='Kerman',
            role=self.ROLES_DICT['OFFICER']
        )
                    
        User.objects.create_user(
            email='billie@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Billie',
            last_name='Kerman',
            role=self.ROLES_DICT['OWNER']
        )   
