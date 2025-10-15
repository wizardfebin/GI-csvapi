from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "email", "age")

    # name: must be non-empty (CharField default handles required but we'll enforce strip)
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name must be a non-empty string.")
        return value.strip()

    # age: integer between 0 and 120
    def validate_age(self, value):
        if not isinstance(value, int):
            # DRF will usually coerce string numeric values to int but check anyway
            raise serializers.ValidationError("Age must be an integer.")
        if value < 0 or value > 120:
            raise serializers.ValidationError("Age must be between 0 and 120.")
        return value

    # email: EmailField already validates format
