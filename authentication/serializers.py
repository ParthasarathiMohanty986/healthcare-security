from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'role', 'department', 'specialization',
            'clearance_level', 'is_emergency_authorized',
            'current_location', 'working_hours_start',
            'working_hours_end'
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims inside the JWT token
        token['role'] = user.role
        token['department'] = user.department
        token['clearance_level'] = user.clearance_level
        token['is_emergency_authorized'] = user.is_emergency_authorized

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user info to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'full_name': self.user.get_full_name(),
            'role': self.user.role,
            'department': self.user.department,
            'clearance_level': self.user.clearance_level,
            'is_emergency_authorized': self.user.is_emergency_authorized,
        }
        return data