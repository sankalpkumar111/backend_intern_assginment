from django.urls import path
from .views import (
    RegisterView,
    TrainSearchView,
    TrainCreateView,
    BookingView,
    MyBookingsView,
    TopRoutesAnalyticsView
)

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),

    # Trains
    path('trains/search/', TrainSearchView.as_view(), name='train-search'),
    path('trains/', TrainCreateView.as_view(), name='train-create'),

    # Bookings
    path('bookings/', BookingView.as_view(), name='book-seat'),
    path('bookings/my/', MyBookingsView.as_view(), name='my-bookings'),
    
    path('analytics/top-routes/', TopRoutesAnalyticsView.as_view(), name='top-routes-analytics'),
]
