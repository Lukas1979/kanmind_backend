from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()  # <- important: use your CustomUser, not Default User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer for registering a new user.
    It defines how incoming data is validated and then a User object is created.
    """
    
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    fullname = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        fullname = validated_data["fullname"]
        email = validated_data["email"]
        password = validated_data["password"]

        user = User.objects.create_user(
            email=email, fullname=fullname, password=password
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    """
    This is a Django REST Framework (DRF) serializer for a user's login.
    It validates the login credentials and authenticates the user.
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        attrs["user"] = user
        return attrs
