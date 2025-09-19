from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from AlertingAndNotificationPlatform.models import User, Team, Alert, AlertRecipient, AlertStatus


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

                # Create sample alerts
                admin_user = User.objects.filter(role='admin').first()
                engineering_team = created_teams.get('Engineering')
                marketing_team = created_teams.get('Marketing')
                john_user = User.objects.filter(
                    email='john.doe@atomicads.com').first()

                if admin_user:
                    alerts_data = [
                        {
                            'title': 'System Maintenance Scheduled',
                            'message_body': 'The system will undergo scheduled maintenance this weekend from 2:00 AM to 4:00 AM UTC. Please save your work and logout before this time.',
                            'severity': 'warning',
                            'delivery_type': 'in_app',
                            'reminder_frequency': 2,
                            'visibility_type': 'organization',
                            'created_by': admin_user
                        },
                        {
                            'title': 'New Feature Release',
                            'message_body': 'We have released a new dashboard feature! Check out the analytics section for improved reporting capabilities.',
                            'severity': 'info',
                            'delivery_type': 'in_app',
                            'reminder_frequency': 4,
                            'visibility_type': 'organization',
                            'created_by': admin_user
                        },
                        {
                            'title': 'Security Update Required',
                            'message_body': 'Please update your password to comply with our new security policy. Passwords must be changed within the next 7 days.',
                            'severity': 'critical',
                            'delivery_type': 'in_app',
                            'reminder_frequency': 1,
                            'visibility_type': 'organization',
                            'expires_at': timezone.now() + timedelta(days=7),
                            'created_by': admin_user
                        },
                        {
                            'title': 'Engineering Team: Code Review Process',
                            'message_body': 'New code review guidelines have been implemented. All pull requests must now have at least 2 approvals before merging.',
                            'severity': 'info',
                            'delivery_type': 'in_app',
                            'reminder_frequency': 6,
                            'visibility_type': 'teams',
                            'created_by': admin_user,
                            'team': engineering_team
                        },
                        {
                            'title': 'Marketing Team: Campaign Launch',
                            'message_body': 'The Q4 marketing campaign launches next week. Please review the campaign materials and prepare your content calendars.',
                            'severity': 'info',
                            'delivery_type': 'in_app',
                            'reminder_frequency': 3,
                            'visibility_type': 'teams',
                            'created_by': admin_user,
                            'team': marketing_team
                        }
                    ]

                    if john_user:
                        alerts_data.append({
                            'title': 'Personal: Training Session Reminder',
                            'message_body': 'You have a mandatory training session scheduled for tomorrow at 10:00 AM. Please ensure you attend.',
                            'severity': 'warning',
                            'delivery_type': 'in_app',
                            'reminder_frequency': 2,
                            'visibility_type': 'users',
                            'created_by': admin_user,
                            'user': john_user
                        })

                    for alert_data in alerts_data:
                        team = alert_data.pop('team', None)
                        user = alert_data.pop('user', None)

                        alert, created = Alert.objects.get_or_create(
                            title=alert_data['title'],
                            defaults=alert_data
                        )

                        if created:
                            # Create recipients for team or user-specific alerts
                            if alert.visibility_type == 'teams' and team:
                                AlertRecipient.objects.get_or_create(
                                    alert=alert, team=team
                                )
                            elif alert.visibility_type == 'users' and user:
                                AlertRecipient.objects.get_or_create(
                                    alert=alert, user=user
                                )

                            # Create AlertStatus entries for all target users
                            target_users = alert.get_target_users()
                            alert_statuses = []
                            for target_user in target_users:
                                if not AlertStatus.objects.filter(alert=alert, user=target_user).exists():
                                    alert_statuses.append(AlertStatus(
                                        alert=alert, user=target_user))

                            if alert_statuses:
                                AlertStatus.objects.bulk_create(alert_statuses)

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created alert: {alert.title}')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Alert already exists: {alert.title}')
                            )

                self.stdout.write(
                    self.style.SUCCESS('\n--- Seed Data Creation Complete ---')
                )
                self.stdout.write(
                    'You can now test the authentication and alert systems with these credentials:')
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
                self.stdout.write(
                    '\nSample alerts have been created for testing!')
                self.stdout.write(
                    'Use the admin users to manage alerts and regular users to view/interact with them.')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating seed data: {str(e)}')
            )
