from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Train(models.Model):
    train_number = models.CharField(max_length=20, unique=True)
    train_name = models.CharField(max_length=200)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    total_sl_seats = models.PositiveIntegerField()
    total_ac3_seats = models.PositiveIntegerField()
    total_ac2_seats = models.PositiveIntegerField()
    total_ac1_seats = models.PositiveIntegerField()

    available_sl_seats = models.PositiveIntegerField()
    available_ac3_seats = models.PositiveIntegerField()
    available_ac2_seats = models.PositiveIntegerField()
    available_ac1_seats = models.PositiveIntegerField()


    def __str__(self):
        return self.train_number + " - " + self.train_name
    
class Booking(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    train=models.ForeignKey(Train, on_delete=models.CASCADE)
    journey_date=models.DateField()
    seats_booked=models.IntegerField()
    booked_at = models.DateTimeField(auto_now_add=True) 
    seat_type = models.CharField(
        max_length=2,
        choices=[
            ("SL", "Sleeper"),
            ("3A", "AC 3 Tier"),
            ("2A", "AC 2 Tier"),
            ("1A", "AC 1 Tier"),
        ]
    )

    def __str__(self):
        return f"Booking by {self.user.email} for {self.train.train_name} on {self.journey_date}"


class TrainSeatAvailability(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="availabilities")
    journey_date = models.DateField()

    available_sl_seats = models.PositiveIntegerField()
    available_ac3_seats = models.PositiveIntegerField()
    available_ac2_seats = models.PositiveIntegerField()
    available_ac1_seats = models.PositiveIntegerField()

    class Meta:
        unique_together = ("train", "journey_date")

    def __str__(self):
        return f"{self.train.train_number} - {self.journey_date}"
