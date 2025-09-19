from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth import authenticate, logout
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
from .models import User, Team, Alert, AlertRecipient, AlertStatus, NotificationDelivery
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer, TeamSerializer,
    TeamDetailSerializer, TeamMemberAssignmentSerializer,
    AlertSerializer, AlertDetailSerializer, UserAlertSerializer,
    AlertStatusSerializer, SnoozeAlertSerializer, ArchiveAlertSerializer,
    AlertFilterSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'team': user.team.name if user.team else None
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'team': user.team.name if user.team else None
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    API endpoint for changing user password
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating teams (Admin only for creation)
    """
    queryset = Team.objects.all().order_by('name')
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Only allow admins to create teams
        """
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                "Only administrators can create teams"
            )
        serializer.save()


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting specific teams
    """
    queryset = Team.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Return detailed serializer for GET requests, basic for others
        """
        if self.request.method == 'GET':
            return TeamDetailSerializer
        return TeamSerializer

    def perform_update(self, serializer):
        """
        Only allow admins to update teams
        """
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                "Only administrators can update teams"
            )
        serializer.save()

    def perform_destroy(self, serializer):
        """
        Only allow admins to delete teams
        Handle team deletion gracefully by reassigning users
        """
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                "Only administrators can delete teams"
            )

        team = self.get_object()
        # Reassign team members to no team before deletion
        team.members.update(team=None)
        team.delete()


class TeamMemberManagementView(APIView):
    """
    API endpoint for managing team members (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, team_id):
        """
        Assign or remove users from a team
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can manage team members'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response(
                {'error': 'Team not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeamMemberAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            action = serializer.validated_data['action']

            # Validate that all user IDs exist
            users = User.objects.filter(id__in=user_ids, is_active=True)
            if len(users) != len(user_ids):
                invalid_ids = set(user_ids) - \
                    set(users.values_list('id', flat=True))
                return Response(
                    {'error': f'Invalid user IDs: {list(invalid_ids)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if action == 'assign':
                # Assign users to the team
                users.update(team=team)
                message = f'Successfully assigned {len(users)} users to team {team.name}'
            else:  # remove
                # Remove users from the team (set team to None)
                team_users = users.filter(team=team)
                team_users.update(team=None)
                message = f'Successfully removed {len(team_users)} users from team {team.name}'

            return Response({
                'message': message,
                'team_id': team_id,
                'team_name': team.name,
                'action': action,
                'affected_users': len(users if action == 'assign' else team_users)
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, team_id):
        """
        Get detailed information about team members
        """
        try:
            team = Team.objects.get(id=team_id)
            serializer = TeamDetailSerializer(team)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response(
                {'error': 'Team not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """
    API endpoint for user dashboard - returns user info and basic stats
    """
    user = request.user

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'team': user.team.name if user.team else None,
            'is_admin': user.is_admin,
        },
        'stats': {
            'total_users': User.objects.count() if user.is_admin else None,
            'total_teams': Team.objects.count() if user.is_admin else None,
        }
    })


# Custom JWT Views with additional response data
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with user data
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Get user from the validated data
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'team': user.team.name if user.team else None
                }
            except User.DoesNotExist:
                pass
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view
    """
    pass


# Alert Management Views

class AlertListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating alerts (Admin only for creation)
    """
    queryset = Alert.objects.filter(is_active=True)
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter alerts based on user role and query parameters
        """
        user = self.request.user
        if user.is_admin:
            # Admins can see all alerts
            queryset = Alert.objects.filter(
                is_active=True).order_by('-created_at')
        else:
            # Regular users can only see alerts they created
            queryset = Alert.objects.filter(
                created_by=user, is_active=True
            ).order_by('-created_at')

        # Apply filters for admin users
        if user.is_admin:
            # Filter by status
            status_filter = self.request.query_params.get('status')
            if status_filter:
                if status_filter == 'archived':
                    queryset = queryset.filter(is_archived=True)
                elif status_filter == 'active':
                    queryset = queryset.filter(
                        is_archived=False
                    ).filter(
                        Q(starts_at__isnull=True) | Q(
                            starts_at__lte=timezone.now())
                    ).filter(
                        Q(expires_at__isnull=True) | Q(
                            expires_at__gt=timezone.now())
                    )
                elif status_filter == 'expired':
                    queryset = queryset.filter(expires_at__lte=timezone.now())
                elif status_filter == 'scheduled':
                    queryset = queryset.filter(
                        starts_at__isnull=False,
                        starts_at__gt=timezone.now()
                    )
                elif status_filter == 'inactive':
                    queryset = queryset.filter(is_active=False)

            # Filter by severity
            severity_filter = self.request.query_params.get('severity')
            if severity_filter:
                queryset = queryset.filter(severity=severity_filter)

            # Filter by audience
            audience_filter = self.request.query_params.get('audience')
            if audience_filter:
                queryset = queryset.filter(visibility_type=audience_filter)

            # Filter by created_by
            created_by_filter = self.request.query_params.get('created_by')
            if created_by_filter:
                queryset = queryset.filter(created_by_id=created_by_filter)

            # Filter by date range
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        """
        Set the creator of the alert and validate permissions
        """
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                "Only administrators can create alerts"
            )
        serializer.save(created_by=self.request.user)


class AlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting specific alerts
    """
    queryset = Alert.objects.filter(is_active=True)
    serializer_class = AlertDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter alerts based on user role
        """
        user = self.request.user
        if user.is_admin:
            return Alert.objects.filter(is_active=True)
        else:
            return Alert.objects.filter(created_by=user, is_active=True)

    def perform_update(self, serializer):
        """
        Only allow admins or creators to update alerts
        """
        alert = self.get_object()
        if not (self.request.user.is_admin or alert.created_by == self.request.user):
            raise permissions.PermissionDenied(
                "You don't have permission to update this alert"
            )
        serializer.save()

    def perform_destroy(self, serializer):
        """
        Soft delete - set is_active to False
        """
        alert = self.get_object()
        if not (self.request.user.is_admin or alert.created_by == self.request.user):
            raise permissions.PermissionDenied(
                "You don't have permission to delete this alert"
            )
        alert.is_active = False
        alert.save()


class ArchiveAlertView(APIView):
    """
    API endpoint for archiving/unarchiving alerts (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, alert_id):
        """
        Archive or unarchive an alert
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can archive alerts'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            alert = Alert.objects.get(id=alert_id)

            serializer = ArchiveAlertSerializer(data=request.data)
            if serializer.is_valid():
                is_archived = serializer.validated_data['is_archived']
                alert.is_archived = is_archived
                alert.save()

                action = 'archived' if is_archived else 'unarchived'
                return Response({
                    'message': f'Alert {action} successfully',
                    'alert_id': alert_id,
                    'is_archived': is_archived
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AlertTrackingView(APIView):
    """
    API endpoint for tracking alert interactions and snooze statistics (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, alert_id):
        """
        Get detailed tracking information for a specific alert
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can access alert tracking'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            alert = Alert.objects.get(id=alert_id)

            # Get all alert statuses for this alert
            alert_statuses = AlertStatus.objects.filter(alert=alert)
            total_recipients = alert_statuses.count()

            if total_recipients == 0:
                return Response({
                    'alert_id': alert_id,
                    'alert_title': alert.title,
                    'total_recipients': 0,
                    'interaction_stats': {},
                    'snooze_stats': {}
                })

            # Calculate interaction statistics
            read_count = alert_statuses.filter(is_read=True).count()
            unread_count = total_recipients - read_count

            # Calculate snooze statistics
            currently_snoozed = alert_statuses.filter(
                is_snoozed=True,
                snoozed_until__gt=timezone.now()
            ).count()

            total_snoozed = alert_statuses.filter(is_snoozed=True).count()

            # Calculate percentages
            read_percentage = round((read_count / total_recipients) * 100, 2)
            snoozed_percentage = round(
                (currently_snoozed / total_recipients) * 100, 2)

            # Check if most users have snoozed (>50%)
            most_users_snoozed = snoozed_percentage > 50

            return Response({
                'alert_id': alert_id,
                'alert_title': alert.title,
                'alert_status': alert.status,
                'total_recipients': total_recipients,
                'interaction_stats': {
                    'read_count': read_count,
                    'unread_count': unread_count,
                    'read_percentage': read_percentage,
                },
                'snooze_stats': {
                    'currently_snoozed': currently_snoozed,
                    'total_ever_snoozed': total_snoozed,
                    'snoozed_percentage': snoozed_percentage,
                    'most_users_snoozed': most_users_snoozed,
                },
                'is_recurring': alert.reminder_enabled and alert.is_currently_active,
            }, status=status.HTTP_200_OK)

        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserAlertListView(generics.ListAPIView):
    """
    API endpoint for users to see their alerts
    """
    serializer_class = UserAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get alerts for the current user based on visibility settings
        """
        user = self.request.user

        # Get alerts based on visibility
        organization_alerts = Q(visibility_type='organization')
        team_alerts = Q(
            visibility_type='teams',
            alert_recipients__team=user.team
        ) if user.team else Q(pk=None)
        user_alerts = Q(
            visibility_type='users',
            alert_recipients__user=user
        )

        alerts = Alert.objects.filter(
            Q(organization_alerts | team_alerts | user_alerts),
            is_active=True,
            is_archived=False
        ).distinct().order_by('-created_at')

        # Only show alerts that have started (or have no start time)
        alerts = alerts.filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=timezone.now())
        )

        # Filter by read status if requested
        read_filter = self.request.query_params.get('read')
        if read_filter is not None:
            is_read = read_filter.lower() == 'true'
            alert_ids = AlertStatus.objects.filter(
                user=user, is_read=is_read
            ).values_list('alert_id', flat=True)
            alerts = alerts.filter(id__in=alert_ids)

        # Filter by severity if requested
        severity = self.request.query_params.get('severity')
        if severity:
            alerts = alerts.filter(severity=severity)

        return alerts

    def list(self, request, *args, **kwargs):
        """
        Override list to include summary statistics
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # Add summary statistics
        user_alert_statuses = AlertStatus.objects.filter(user=request.user)
        summary = {
            'total_alerts': queryset.count(),
            'unread_alerts': user_alert_statuses.filter(is_read=False).count(),
            'snoozed_alerts': user_alert_statuses.filter(
                is_snoozed=True,
                snoozed_until__gt=timezone.now()
            ).count(),
        }

        return Response({
            'summary': summary,
            'alerts': serializer.data
        })


class MarkAlertAsReadView(APIView):
    """
    API endpoint for users to mark alerts as read
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, alert_id):
        """
        Mark an alert as read for the current user
        """
        try:
            alert = Alert.objects.get(id=alert_id, is_active=True)

            # Check if user should have access to this alert
            user = request.user
            target_users = alert.get_target_users()
            if user not in target_users:
                return Response(
                    {'error': 'You do not have access to this alert'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create alert status
            alert_status, created = AlertStatus.objects.get_or_create(
                alert=alert,
                user=user,
                defaults={'is_read': True}
            )

            if not created and not alert_status.is_read:
                alert_status.is_read = True
                alert_status.save()

            return Response({
                'message': 'Alert marked as read',
                'alert_id': alert_id,
                'is_read': True
            }, status=status.HTTP_200_OK)

        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SnoozeAlertView(APIView):
    """
    API endpoint for users to snooze alerts
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, alert_id):
        """
        Snooze an alert for the current user
        """
        try:
            alert = Alert.objects.get(id=alert_id, is_active=True)

            # Check if user should have access to this alert
            user = request.user
            target_users = alert.get_target_users()
            if user not in target_users:
                return Response(
                    {'error': 'You do not have access to this alert'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = SnoozeAlertSerializer(data=request.data)
            if serializer.is_valid():
                hours = serializer.validated_data['hours']
                snooze_until = timezone.now() + timedelta(hours=hours)

                # Get or create alert status
                alert_status, created = AlertStatus.objects.get_or_create(
                    alert=alert,
                    user=user,
                    defaults={
                        'is_snoozed': True,
                        'snoozed_until': snooze_until
                    }
                )

                if not created:
                    alert_status.is_snoozed = True
                    alert_status.snoozed_until = snooze_until
                    alert_status.save()

                return Response({
                    'message': f'Alert snoozed for {hours} hours',
                    'alert_id': alert_id,
                    'snoozed_until': snooze_until
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UnsnoozeAlertView(APIView):
    """
    API endpoint for users to unsnooze alerts
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, alert_id):
        """
        Unsnooze an alert for the current user
        """
        try:
            alert = Alert.objects.get(id=alert_id, is_active=True)

            # Check if user should have access to this alert
            user = request.user
            target_users = alert.get_target_users()
            if user not in target_users:
                return Response(
                    {'error': 'You do not have access to this alert'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Update alert status
            try:
                alert_status = AlertStatus.objects.get(alert=alert, user=user)
                alert_status.is_snoozed = False
                alert_status.snoozed_until = None
                alert_status.save()

                return Response({
                    'message': 'Alert unsnoozed successfully',
                    'alert_id': alert_id
                }, status=status.HTTP_200_OK)

            except AlertStatus.DoesNotExist:
                return Response(
                    {'message': 'Alert was not snoozed'},
                    status=status.HTTP_200_OK
                )

        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ToggleAlertReminderView(APIView):
    """
    API endpoint for enabling/disabling reminders for an alert (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, alert_id):
        """
        Toggle reminder enabled status for an alert
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can toggle alert reminders'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            alert = Alert.objects.get(id=alert_id, is_active=True)

            # Toggle the reminder_enabled status
            alert.reminder_enabled = not alert.reminder_enabled
            alert.save()

            status_text = 'enabled' if alert.reminder_enabled else 'disabled'
            return Response({
                'message': f'Alert reminders {status_text} successfully',
                'alert_id': alert_id,
                'reminder_enabled': alert.reminder_enabled
            }, status=status.HTTP_200_OK)

        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def alert_stats(request):
    """
    API endpoint for alert statistics (Admin only)
    """
    if not request.user.is_admin:
        return Response(
            {'error': 'Only administrators can access alert statistics'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get basic alert statistics
    total_alerts = Alert.objects.filter(is_active=True).count()
    active_alerts = Alert.objects.filter(
        is_active=True,
        is_archived=False
    ).filter(
        Q(starts_at__isnull=True) | Q(starts_at__lte=timezone.now())
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).count()

    expired_alerts = Alert.objects.filter(
        is_active=True,
        expires_at__lte=timezone.now()
    ).count()

    archived_alerts = Alert.objects.filter(
        is_active=True,
        is_archived=True
    ).count()

    scheduled_alerts = Alert.objects.filter(
        is_active=True,
        is_archived=False,
        starts_at__isnull=False,
        starts_at__gt=timezone.now()
    ).count()

    reminders_enabled = Alert.objects.filter(
        is_active=True,
        reminder_enabled=True
    ).count()

    reminders_disabled = Alert.objects.filter(
        is_active=True,
        reminder_enabled=False
    ).count()

    # Alerts by severity
    severity_stats = Alert.objects.filter(is_active=True).values(
        'severity'
    ).annotate(count=Count('id'))

    # Recent alerts (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_alerts = Alert.objects.filter(
        is_active=True,
        created_at__gte=week_ago
    ).count()

    # Alert interaction statistics
    total_alert_statuses = AlertStatus.objects.count()
    read_statuses = AlertStatus.objects.filter(is_read=True).count()
    snoozed_statuses = AlertStatus.objects.filter(
        is_snoozed=True,
        snoozed_until__gt=timezone.now()
    ).count()

    return Response({
        'alert_stats': {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'expired_alerts': expired_alerts,
            'archived_alerts': archived_alerts,
            'scheduled_alerts': scheduled_alerts,
            'recent_alerts': recent_alerts,
        },
        'reminder_stats': {
            'reminders_enabled': reminders_enabled,
            'reminders_disabled': reminders_disabled,
        },
        'severity_breakdown': {item['severity']: item['count'] for item in severity_stats},
        'interaction_stats': {
            'total_recipients': total_alert_statuses,
            'read_count': read_statuses,
            'unread_count': total_alert_statuses - read_statuses,
            'snoozed_count': snoozed_statuses,
            'read_percentage': round((read_statuses / total_alert_statuses * 100), 2) if total_alert_statuses > 0 else 0
        }
    })


# Notification Delivery Views

class SendNotificationView(APIView):
    """
    API endpoint for sending notifications manually (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, alert_id):
        """
        Send notifications for a specific alert
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can send notifications'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            alert = Alert.objects.get(id=alert_id, is_active=True)
        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Import notification service
        from .notification_system import notification_service

        # Get target users for this alert
        target_users = alert.get_target_users()

        if not target_users.exists():
            return Response(
                {'error': 'No target users found for this alert'},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        for user in target_users:
            # Determine recipient based on delivery type
            if alert.delivery_type == 'email':
                recipient = user.email
            elif alert.delivery_type == 'sms':
                recipient = user.phone_number
                if not recipient:
                    results.append({
                        'user_id': user.id,
                        'user_email': user.email,
                        'status': 'failed',
                        'error': 'No phone number available'
                    })
                    continue
            else:  # in_app
                recipient = str(user.id)

            # Prepare metadata
            metadata = {
                'alert_id': alert.id,
                'severity': alert.severity,
                'visibility_type': alert.visibility_type,
                'sender': request.user.email
            }

            # Send notification
            result = notification_service.send_notification(
                delivery_type=alert.delivery_type,
                recipient=recipient,
                title=alert.title,
                message=alert.message_body,
                metadata=metadata
            )

            # Create delivery log
            delivery_log = NotificationDelivery.objects.create(
                alert=alert,
                user=user,
                delivery_type=alert.delivery_type,
                recipient=recipient,
                status=result['status'],
                message_id=result.get('message_id'),
                error_message=result.get('error'),
                attempt_count=1,
                last_attempt_at=timezone.now(),
                delivered_at=timezone.now() if result['status'] in [
                    'sent', 'delivered'] else None,
                metadata=metadata
            )

            results.append({
                'user_id': user.id,
                'user_email': user.email,
                'delivery_id': delivery_log.id,
                'status': result['status'],
                'channel': result['channel'],
                'recipient': recipient,
                'error': result.get('error')
            })

        # Get delivery statistics
        delivery_stats = notification_service.get_delivery_stats()

        return Response({
            'message': f'Notification sending completed for alert: {alert.title}',
            'alert_id': alert_id,
            'total_recipients': len(target_users),
            'delivery_results': results,
            'delivery_stats': delivery_stats
        }, status=status.HTTP_200_OK)


class NotificationDeliveryStatusView(APIView):
    """
    API endpoint for checking notification delivery status (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, alert_id):
        """
        Get delivery status for all notifications of a specific alert
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can view delivery status'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            alert = Alert.objects.get(id=alert_id, is_active=True)
        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all delivery logs for this alert
        delivery_logs = NotificationDelivery.objects.filter(
            alert=alert).order_by('-created_at')

        # Prepare response data
        delivery_data = []
        for log in delivery_logs:
            delivery_data.append({
                'id': log.id,
                'user': {
                    'id': log.user.id,
                    'email': log.user.email,
                    'full_name': log.user.full_name
                },
                'delivery_type': log.delivery_type,
                'recipient': log.recipient,
                'status': log.status,
                'message_id': log.message_id,
                'error_message': log.error_message,
                'attempt_count': log.attempt_count,
                'last_attempt_at': log.last_attempt_at,
                'delivered_at': log.delivered_at,
                'created_at': log.created_at
            })

        # Calculate delivery statistics
        total_deliveries = delivery_logs.count()
        if total_deliveries > 0:
            sent_count = delivery_logs.filter(
                status__in=['sent', 'delivered']).count()
            failed_count = delivery_logs.filter(status='failed').count()
            pending_count = delivery_logs.filter(status='pending').count()

            delivery_summary = {
                'total_deliveries': total_deliveries,
                'sent_count': sent_count,
                'failed_count': failed_count,
                'pending_count': pending_count,
                'success_rate': round((sent_count / total_deliveries) * 100, 2)
            }
        else:
            delivery_summary = {
                'total_deliveries': 0,
                'sent_count': 0,
                'failed_count': 0,
                'pending_count': 0,
                'success_rate': 0
            }

        return Response({
            'alert_id': alert_id,
            'alert_title': alert.title,
            'delivery_summary': delivery_summary,
            'delivery_logs': delivery_data
        }, status=status.HTTP_200_OK)


class RetryFailedNotificationsView(APIView):
    """
    API endpoint for retrying failed notifications (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, alert_id):
        """
        Retry failed notifications for a specific alert
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can retry notifications'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            alert = Alert.objects.get(id=alert_id, is_active=True)
        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Import notification service
        from .notification_system import notification_service

        # Get failed delivery logs
        failed_deliveries = NotificationDelivery.objects.filter(
            alert=alert,
            status='failed'
        )

        if not failed_deliveries.exists():
            return Response(
                {'message': 'No failed deliveries found to retry'},
                status=status.HTTP_200_OK
            )

        retry_results = []
        for delivery_log in failed_deliveries:
            # Retry the notification
            metadata = delivery_log.metadata or {}
            metadata['retry_attempt'] = delivery_log.attempt_count + 1

            result = notification_service.send_notification(
                delivery_type=delivery_log.delivery_type,
                recipient=delivery_log.recipient,
                title=alert.title,
                message=alert.message_body,
                metadata=metadata
            )

            # Update delivery log
            delivery_log.status = result['status']
            delivery_log.attempt_count += 1
            delivery_log.last_attempt_at = timezone.now()
            if result['status'] in ['sent', 'delivered']:
                delivery_log.delivered_at = timezone.now()
                delivery_log.error_message = None
            else:
                delivery_log.error_message = result.get('error')

            if result.get('message_id'):
                delivery_log.message_id = result['message_id']

            delivery_log.save()

            retry_results.append({
                'delivery_id': delivery_log.id,
                'user_email': delivery_log.user.email,
                'status': result['status'],
                'attempt_count': delivery_log.attempt_count,
                'error': result.get('error')
            })

        return Response({
            'message': f'Retry completed for {len(failed_deliveries)} failed notifications',
            'alert_id': alert_id,
            'retry_results': retry_results
        }, status=status.HTTP_200_OK)


# Scheduler Management Views

class SchedulerStatusView(APIView):
    """
    API endpoint for checking scheduler status (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get current status of the task scheduler
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can view scheduler status'},
                status=status.HTTP_403_FORBIDDEN
            )

        from .scheduler import scheduler

        status_data = scheduler.get_status()

        return Response({
            'scheduler_status': status_data,
            'cron_setup_guide': scheduler.get_cron_setup_guide()
        }, status=status.HTTP_200_OK)


class SchedulerControlView(APIView):
    """
    API endpoint for controlling the scheduler (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Start or stop the scheduler
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can control the scheduler'},
                status=status.HTTP_403_FORBIDDEN
            )

        action = request.data.get('action')

        if action not in ['start', 'stop']:
            return Response(
                {'error': 'Invalid action. Use "start" or "stop"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .scheduler import scheduler

        if action == 'start':
            scheduler.start()
            message = 'Scheduler started successfully'
        else:
            scheduler.stop()
            message = 'Scheduler stopped successfully'

        return Response({
            'message': message,
            'action': action,
            'scheduler_running': scheduler.running
        }, status=status.HTTP_200_OK)


class RunTaskView(APIView):
    """
    API endpoint for running scheduled tasks manually (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Run a specific task immediately
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can run tasks'},
                status=status.HTTP_403_FORBIDDEN
            )

        task_name = request.data.get('task_name')

        if not task_name:
            return Response(
                {'error': 'task_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .scheduler import scheduler

        if task_name not in scheduler.tasks:
            available_tasks = list(scheduler.tasks.keys())
            return Response(
                {
                    'error': f'Task "{task_name}" not found',
                    'available_tasks': available_tasks
                },
                status=status.HTTP_404_NOT_FOUND
            )

        result = scheduler.run_task_now(task_name)

        if result:
            return Response({
                'message': f'Task "{task_name}" executed',
                'task_result': {
                    'success': result.success,
                    'message': result.message,
                    'duration': result.duration,
                    'timestamp': result.timestamp.isoformat()
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'Failed to execute task "{task_name}"'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
