from django.core.management.base import BaseCommand
from django.db import transaction
from AlertingAndNotificationPlatform.models import User, Team


class Command(BaseCommand):
    help = 'Create seed data for testing the authentication system'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Create teams
                teams_data = [
                    {
                        'name': 'Engineering',
                        'description': 'Software development and technical operations team'
                    },
                    {
                        'name': 'Marketing',
                        'description': 'Marketing and communications team'
                    },
                    {
                        'name': 'Sales',
                        'description': 'Sales and business development team'
                    },
                    {
                        'name': 'HR',
                        'description': 'Human resources and people operations team'
                    }
                ]

                created_teams = {}
                for team_data in teams_data:
                    team, created = Team.objects.get_or_create(
                        name=team_data['name'],
                        defaults={'description': team_data['description']}
                    )
                    created_teams[team.name] = team
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Created team: {team.name}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Team already exists: {team.name}')
                        )

                # Create users
                users_data = [
                    {
                        'username': 'admin_user',
                        'email': 'admin@atomicads.com',
                        'password': 'admin123456',
                        'first_name': 'Admin',
                        'last_name': 'User',
                        'role': 'admin',
                        'team': 'Engineering'
                    },
                    {
                        'username': 'john_doe',
                        'email': 'john.doe@atomicads.com',
                        'password': 'user123456',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'user',
                        'team': 'Engineering'
                    },
                    {
                        'username': 'jane_smith',
                        'email': 'jane.smith@atomicads.com',
                        'password': 'user123456',
                        'first_name': 'Jane',
                        'last_name': 'Smith',
                        'role': 'user',
                        'team': 'Marketing'
                    },
                    {
                        'username': 'bob_wilson',
                        'email': 'bob.wilson@atomicads.com',
                        'password': 'user123456',
                        'first_name': 'Bob',
                        'last_name': 'Wilson',
                        'role': 'user',
                        'team': 'Sales'
                    },
                    {
                        'username': 'alice_brown',
                        'email': 'alice.brown@atomicads.com',
                        'password': 'user123456',
                        'first_name': 'Alice',
                        'last_name': 'Brown',
                        'role': 'admin',
                        'team': 'HR'
                    }
                ]

                for user_data in users_data:
                    if not User.objects.filter(email=user_data['email']).exists():
                        team = created_teams.get(user_data['team'])
                        user = User.objects.create_user(
                            username=user_data['username'],
                            email=user_data['email'],
                            password=user_data['password'],
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name'],
                            role=user_data['role'],
                            team=team
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'Created user: {user.email}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'User already exists: {user_data["email"]}')
                        )

                self.stdout.write(
                    self.style.SUCCESS('\n--- Seed Data Creation Complete ---')
                )
                self.stdout.write(
                    'You can now test the authentication system with these credentials:')
                self.stdout.write('\nAdmin Users:')
                self.stdout.write(
                    'Email: admin@atomicads.com | Password: admin123456')
                self.stdout.write(
                    'Email: alice.brown@atomicads.com | Password: user123456')
                self.stdout.write('\nRegular Users:')
                self.stdout.write(
                    'Email: john.doe@atomicads.com | Password: user123456')
                self.stdout.write(
                    'Email: jane.smith@atomicads.com | Password: user123456')
                self.stdout.write(
                    'Email: bob.wilson@atomicads.com | Password: user123456')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating seed data: {str(e)}')
            )
