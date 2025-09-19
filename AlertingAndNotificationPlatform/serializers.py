from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import User, Team, Alert, AlertRecipient, AlertStatus


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for Team model
    """
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'description',
                  'member_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.members.count()


class TeamDetailSerializer(TeamSerializer):
    """
    Detailed serializer for Team model with member information
    """
    members = serializers.SerializerMethodField()

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ['members']

    def get_members(self, obj):
        return [
            {
                'id': member.id,
                'email': member.email,
                'full_name': member.full_name,
                'role': member.role,
                'is_active': member.is_active
            }
            for member in obj.members.all()
        ]


class TeamMemberAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning/removing team members
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of user IDs to assign to this team"
    )
    action = serializers.ChoiceField(
        choices=[('assign', 'Assign'), ('remove', 'Remove')],
        default='assign',
        help_text="Action to perform: assign users to team or remove them"
    )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    team_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'confirm_password', 'role', 'team_name',
            'phone_number'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs

    def validate_email(self, value):
        """
        Validate email uniqueness
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def create(self, validated_data):
        """
        Create user with validated data
        """
        # Remove confirm_password and team_name from validated_data
        validated_data.pop('confirm_password', None)
        team_name = validated_data.pop('team_name', None)

        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'user'),
            phone_number=validated_data.get('phone_number', '')
        )

        # Assign team if provided
        if team_name:
            try:
                team = Team.objects.get(name=team_name)
                user.team = team
                user.save()
            except Team.DoesNotExist:
                pass  # Team doesn't exist, skip assignment

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        """
        Validate user credentials
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Find user by email and verify password
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    if not user.is_active:
                        raise serializers.ValidationError(
                            'User account is disabled.')
                    attrs['user'] = user
                    return attrs
                else:
                    raise serializers.ValidationError(
                        'Invalid email or password.')
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError(
                'Must include email and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    team = TeamSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'team', 'phone_number', 'is_active',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    confirm_new_password = serializers.CharField(
        style={'input_type': 'password'})

    def validate(self, attrs):
        """
        Validate password change
        """
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError(
                "New password fields didn't match.")
        return attrs

    def validate_old_password(self, value):
        """
        Validate old password
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class AlertRecipientSerializer(serializers.ModelSerializer):
    """
    Serializer for AlertRecipient model
    """
    team_name = serializers.CharField(source='team.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(
        source='user.full_name', read_only=True)

    class Meta:
        model = AlertRecipient
        fields = ['id', 'team', 'team_name', 'user',
                  'user_email', 'user_full_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class AlertStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for AlertStatus model
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(
        source='user.full_name', read_only=True)
    is_snoozed_active = serializers.ReadOnlyField()

    class Meta:
        model = AlertStatus
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'is_read',
            'is_snoozed', 'snoozed_until', 'is_snoozed_active',
            'last_reminded_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user',
                            'last_reminded_at', 'created_at', 'updated_at']


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Alert model - used for creation and listing
    """
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True)
    recipients = AlertRecipientSerializer(
        source='alert_recipients', many=True, read_only=True)
    recipient_teams = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False)
    recipient_users = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False)
    is_expired = serializers.ReadOnlyField()
    is_started = serializers.ReadOnlyField()
    is_currently_active = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message_body', 'severity', 'delivery_type',
            'reminder_frequency', 'visibility_type', 'is_active', 'is_archived',
            'starts_at', 'expires_at', 'reminder_enabled', 'created_by', 'created_by_name',
            'recipients', 'recipient_teams', 'recipient_users', 'is_expired',
            'is_started', 'is_currently_active', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Validate alert data
        """
        visibility_type = attrs.get('visibility_type')
        recipient_teams = attrs.get('recipient_teams', [])
        recipient_users = attrs.get('recipient_users', [])

        if visibility_type == 'teams' and not recipient_teams:
            raise serializers.ValidationError(
                "recipient_teams is required when visibility_type is 'teams'")

        if visibility_type == 'users' and not recipient_users:
            raise serializers.ValidationError(
                "recipient_users is required when visibility_type is 'users'")

        if visibility_type == 'organization' and (recipient_teams or recipient_users):
            raise serializers.ValidationError(
                "recipient_teams and recipient_users should not be provided when visibility_type is 'organization'")

        # Validate start and expiration dates
        starts_at = attrs.get('starts_at')
        expires_at = attrs.get('expires_at')

        if starts_at and starts_at <= timezone.now():
            raise serializers.ValidationError(
                "starts_at must be in the future")

        if expires_at and expires_at <= timezone.now():
            raise serializers.ValidationError(
                "expires_at must be in the future")

        if starts_at and expires_at and starts_at >= expires_at:
            raise serializers.ValidationError(
                "starts_at must be before expires_at")

        return attrs

    def create(self, validated_data):
        """
        Create alert with recipients
        """
        recipient_teams = validated_data.pop('recipient_teams', [])
        recipient_users = validated_data.pop('recipient_users', [])

        alert = Alert.objects.create(**validated_data)

        # Create recipients based on visibility type
        if alert.visibility_type == 'teams':
            for team_id in recipient_teams:
                try:
                    team = Team.objects.get(id=team_id)
                    AlertRecipient.objects.create(alert=alert, team=team)
                except Team.DoesNotExist:
                    pass

        elif alert.visibility_type == 'users':
            for user_id in recipient_users:
                try:
                    user = User.objects.get(id=user_id)
                    AlertRecipient.objects.create(alert=alert, user=user)
                except User.DoesNotExist:
                    pass

        # Create AlertStatus entries for all target users
        target_users = alert.get_target_users()
        alert_statuses = [
            AlertStatus(alert=alert, user=user) for user in target_users
        ]
        AlertStatus.objects.bulk_create(alert_statuses, ignore_conflicts=True)

        return alert


class AlertDetailSerializer(AlertSerializer):
    """
    Detailed serializer for Alert model - includes status information
    """
    alert_statuses = AlertStatusSerializer(many=True, read_only=True)
    total_recipients = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta(AlertSerializer.Meta):
        fields = AlertSerializer.Meta.fields + [
            'alert_statuses', 'total_recipients', 'read_count', 'unread_count'
        ]

    def get_total_recipients(self, obj):
        return obj.alert_statuses.count()

    def get_read_count(self, obj):
        return obj.alert_statuses.filter(is_read=True).count()

    def get_unread_count(self, obj):
        return obj.alert_statuses.filter(is_read=False).count()


class UserAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for alerts from user's perspective
    """
    alert_status = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_started = serializers.ReadOnlyField()
    is_currently_active = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message_body', 'severity', 'delivery_type',
            'reminder_frequency', 'reminder_enabled', 'created_by_name', 'is_expired',
            'is_started', 'is_currently_active', 'status', 'starts_at', 'expires_at',
            'created_at', 'alert_status'
        ]

    def get_alert_status(self, obj):
        """
        Get the alert status for the current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                status = obj.alert_statuses.get(user=request.user)
                return {
                    'is_read': status.is_read,
                    'is_snoozed': status.is_snoozed,
                    'snoozed_until': status.snoozed_until,
                    'is_snoozed_active': status.is_snoozed_active,
                }
            except AlertStatus.DoesNotExist:
                return {
                    'is_read': False,
                    'is_snoozed': False,
                    'snoozed_until': None,
                    'is_snoozed_active': False,
                }
        return None


class SnoozeAlertSerializer(serializers.Serializer):
    """
    Serializer for snoozing alerts
    """
    hours = serializers.IntegerField(
        min_value=1, max_value=168, default=2)  # 1 hour to 1 week


class ArchiveAlertSerializer(serializers.Serializer):
    """
    Serializer for archiving/unarchiving alerts
    """
    is_archived = serializers.BooleanField()


class AlertFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering alerts in admin views
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
        ('inactive', 'Inactive'),
    ]

    AUDIENCE_CHOICES = [
        ('organization', 'Entire Organization'),
        ('teams', 'Specific Teams'),
        ('users', 'Specific Users'),
    ]

    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    severity = serializers.ChoiceField(
        choices=Alert.SEVERITY_CHOICES, required=False)
    audience = serializers.ChoiceField(
        choices=AUDIENCE_CHOICES, required=False)
    created_by = serializers.IntegerField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
