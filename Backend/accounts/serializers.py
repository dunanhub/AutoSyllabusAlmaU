from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_staff']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name', max_length=150, required=False, allow_blank=True)
    lastName = serializers.CharField(source='last_name', max_length=150, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'firstName', 'lastName', 'is_staff']
        read_only_fields = ['id', 'email', 'is_staff']


class RegisterSerializer(serializers.Serializer):
    firstName = serializers.CharField(source='first_name', max_length=150)
    lastName = serializers.CharField(source='last_name', max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    passwordConfirm = serializers.CharField(write_only=True)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return email

    def validate(self, attrs):
        password = attrs.get('password', '')
        if password != attrs.pop('passwordConfirm', ''):
            raise serializers.ValidationError({'passwordConfirm': 'Пароли не совпадают.'})

        candidate = User(
            email=attrs.get('email', ''),
            first_name=attrs.get('first_name', ''),
            last_name=attrs.get('last_name', ''),
        )
        validate_password(password, user=candidate)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RegisterResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    access = serializers.CharField()
    refresh = serializers.CharField()
