
from django.db import models
from django.db.models import ForeignKey, ManyToManyField
# Create your models here.
class Rooms(models.Model):
    name = models.CharField(max_length=225)
    capacity = models.IntegerField()
    projector = models.BooleanField()
    availability = models.BooleanField()

class Room_reservation(models.Model):
    date = models.DateField()
    # id_room = models.IntegerField()
    comment = models.CharField(max_length=225)
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE)

    # one room can have many all-day bookings (every other day)

    # In the Meta class of the Room_reservation model, we define the unique_together attribute to specify
    # that the identical id_room date should be unique for each reservation.
    # This will prevent duplicate bookings for the same room on the same day.

    class Meta:
        # Ensure that each room can have multiple bookings on different days
        unique_together = ('date', 'room',)

