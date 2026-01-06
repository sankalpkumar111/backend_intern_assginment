from rest_framework import serializers
from .models import Train, Booking
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = [
            "id",
            "train_number",
            "train_name",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "available_sl_seats",
            "available_ac3_seats",
            "available_ac2_seats",
            "available_ac1_seats",
        ]
        
class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['train', 'journey_date', 'seats_booked']

class BookingListSerializer(serializers.ModelSerializer):
    train_number = serializers.CharField(source="train.train_number", read_only=True)
    train_name = serializers.CharField(source="train.train_name", read_only=True)
    source = serializers.CharField(source="train.source", read_only=True)
    destination = serializers.CharField(source="train.destination", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "train_number",
            "train_name",
            "source",
            "destination",
            "journey_date",
            "seat_type",
            "seats_booked",
            "booked_at",
        ]