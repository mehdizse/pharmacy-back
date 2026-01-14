from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription des utilisateurs
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                "Les mots de passe ne correspondent pas"
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer pour la connexion des utilisateurs
    """
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Identifiants invalides',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Ce compte est désactivé',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        
        else:
            raise serializers.ValidationError(
                'Les champs username et password sont requis',
                code='authorization'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer pour le profil utilisateur
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'phone', 'is_active',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'role', 'date_joined', 
            'last_login', 'created_at', 'updated_at'
        ]


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des utilisateurs (admin seulement)
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'date_joined'
        ]
