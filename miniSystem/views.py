from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db import transaction
from datetime import date
from .mongo import search_logs_collection
from django.contrib.auth.models import User
from .models import Train, Booking,TrainSeatAvailability
from .serializers import (
    RegisterSerializer,
    TrainSerializer,
    BookingCreateSerializer,
    BookingListSerializer
)

import time
from .mongo import search_logs_collection


# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )
class TrainSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        source = request.GET.get('source')
        destination = request.GET.get('destination')

        if not source or not destination:
            return Response(
                {"error": "source and destination are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        trains = Train.objects.filter(
            source__iexact=source,
            destination__iexact=destination
        )

        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data)

class TrainCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = TrainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        train_id = request.data.get("train")
        seat_type = request.data.get("seat_type")
        seats = request.data.get("seats_booked")
        journey_date = request.data.get("journey_date")

        #  BASIC VALIDATION 
        if not all([train_id, seat_type, seats, journey_date]):
            return Response(
                {"error": "train, seat_type, seats_booked and journey_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            seats = int(seats)
            if seats <= 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "seats_booked must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            journey_date = date.fromisoformat(journey_date)
        except ValueError:
            return Response(
                {"error": "Invalid journey_date format (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                #  LOCK TRAIN 
                train = Train.objects.select_for_update().get(id=train_id)

                # GET / CREATE DATE AVAILABILITY 
                availability, _ = TrainSeatAvailability.objects.select_for_update().get_or_create(
                    train=train,
                    journey_date=journey_date,
                    defaults={
                        "available_sl_seats": train.total_sl_seats,
                        "available_ac3_seats": train.total_ac3_seats,
                        "available_ac2_seats": train.total_ac2_seats,
                        "available_ac1_seats": train.total_ac1_seats,
                    }
                )

                # SEAT DEDUCTION
                if seat_type == "SL":
                    if availability.available_sl_seats < seats:
                        return Response(
                            {"error": "Not enough SL seats available"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    availability.available_sl_seats -= seats

                elif seat_type == "3A":
                    if availability.available_ac3_seats < seats:
                        return Response(
                            {"error": "Not enough 3A seats available"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    availability.available_ac3_seats -= seats

                elif seat_type == "2A":
                    if availability.available_ac2_seats < seats:
                        return Response(
                            {"error": "Not enough 2A seats available"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    availability.available_ac2_seats -= seats

                elif seat_type == "1A":
                    if availability.available_ac1_seats < seats:
                        return Response(
                            {"error": "Not enough 1A seats available"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    availability.available_ac1_seats -= seats

                else:
                    return Response(
                        {"error": "Invalid seat_type"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                availability.save()

                #  CREATE BOOKING
                booking = Booking.objects.create(
                    user=request.user,
                    train=train,
                    journey_date=journey_date,
                    seats_booked=seats,
                    seat_type=seat_type
                )

            return Response(
                BookingListSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )

        except Train.DoesNotExist:
            return Response(
                {"error": "Train not found"},
                status=status.HTTP_404_NOT_FOUND
            )
class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by("-booked_at")
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrainSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        start_time = time.time()

        train_number = request.GET.get("train_number")
        source = request.GET.get("source")
        destination = request.GET.get("destination")
        journey_date = request.GET.get("date")

        if not journey_date:
            return Response(
                {"error": "date is required (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            journey_date = date.fromisoformat(journey_date)
        except ValueError:
            return Response(
                {"error": "Invalid date format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  SEARCH
        if train_number:
            trains = Train.objects.filter(train_number__iexact=train_number)
            search_params = {"train_number": train_number, "date": str(journey_date)}

        elif source and destination:
            trains = Train.objects.filter(
                source__icontains=source,
                destination__icontains=destination
            )
            search_params = {
                "source": source,
                "destination": destination,
                "date": str(journey_date)
            }

        else:
            return Response(
                {"error": "Provide train_number OR source & destination"},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []

        for train in trains:
            availability, _ = TrainSeatAvailability.objects.get_or_create(
                train=train,
                journey_date=journey_date,
                defaults={
                    "available_sl_seats": train.total_sl_seats,
                    "available_ac3_seats": train.total_ac3_seats,
                    "available_ac2_seats": train.total_ac2_seats,
                    "available_ac1_seats": train.total_ac1_seats,
                }
            )

            results.append({
                "id": train.id,
                "train_number": train.train_number,
                "train_name": train.train_name,
                "source": train.source,
                "destination": train.destination,
                "departure_time": train.departure_time,
                "arrival_time": train.arrival_time,
                "available_sl_seats": availability.available_sl_seats,
                "available_ac3_seats": availability.available_ac3_seats,
                "available_ac2_seats": availability.available_ac2_seats,
                "available_ac1_seats": availability.available_ac1_seats,
            })

        # - MONGO LOG 
        try:
            search_logs_collection.insert_one({
                "endpoint": "/api/trains/search/",
                "params": search_params,
                "execution_time": round(time.time() - start_time, 4)
            })
        except Exception:
            pass

        return Response(results, status=status.HTTP_200_OK)

class TopRoutesAnalyticsView(APIView):
    permission_classes = [IsAdminUser]  

    def get(self, request):
        pipeline = [
            {
                "$match": {
                    "endpoint": "/api/trains/search/",
                    "params.source": {"$exists": True},
                    "params.destination": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": {
                        "source": "$params.source",
                        "destination": "$params.destination"
                    },
                    "search_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"search_count": -1}
            },
            {
                "$limit": 5
            }
        ]

        results = list(search_logs_collection.aggregate(pipeline))

        response_data = [
            {
                "source": r["_id"]["source"],
                "destination": r["_id"]["destination"],
                "search_count": r["search_count"]
            }
            for r in results
        ]

        return Response(response_data, status=status.HTTP_200_OK)