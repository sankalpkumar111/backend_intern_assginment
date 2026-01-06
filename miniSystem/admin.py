from django.contrib import admin
from .models import Train, Booking,TrainSeatAvailability
# Register your models here.

admin.site.register(Train)  
admin.site.register(Booking)
admin.site.register(TrainSeatAvailability)
