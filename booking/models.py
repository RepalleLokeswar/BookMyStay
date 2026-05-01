from django.db import models
from django.contrib.auth.models import User

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='hotels/')

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"

class Booking(models.Model):
    STATUS = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    razorpay_order_id = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.room} - {self.status}"
