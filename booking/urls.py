from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/<int:hotel_id>/', views.rooms, name='rooms'),
    path('book/<int:room_id>/', views.book_room, name='book'),
    path('payment-success/', views.payment_success, name='payment_success'),

    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]
