
# This Django app provides functionality to manage and book rooms.
# Users can add new rooms, edit existing rooms, view room details, make room reservations,
# and search for rooms based on various criteria such as name, projector availability, and capacity range.
# The application helps in the effective management and use of available space for various purposes.


from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from rezervation.models import Rooms, Room_reservation
from django.contrib import messages
from datetime import date

def new_room(request):
    if request.method == "POST":
        # Downloading data from the form
        name = request.POST.get('name')
        capacity = int(request.POST.get('capacity', 0))
        projector = request.POST.get('projector', False)
        availability = request.POST.get('availability', False)

        if name and not Rooms.objects.filter(name=name).exists() and capacity > 0:

            new_room = Rooms(name = name, capacity = capacity, projector = projector, availability = availability)
            new_room.save()

            return redirect('/rooms/')
        else:
            if not name:
                messages.error(request, "Nie podano nazwy sali.")
            if Rooms.objects.filter(name=name).exists():
                messages.error(request, "Sala o tej nazwie już istnieje.")
            if capacity <= 0:
                messages.error(request, "Pojemność sali musi być większa od 0.")
            return HttpResponseRedirect('/rooms/')

    return render(request, 'new_room.html')


def edit_room(request, id):
    if request.method == 'GET':
        # extract the room by id and transfer the data to the form
        room = Rooms.objects.get(pk=id)
        context = {
            "room": room
        }
        return render(request, "edit_rooms.html", context)

    if request.method == "POST":

        name = request.POST.get('name')
        capacity = int(request.POST.get('capacity', 0))
        projector = request.POST.get('projector', False)
        availability = request.POST.get('availability', False)

        # checking condition, saving data and redirecting
        if name and capacity > 0:
            room = Rooms.objects.get(pk=id)
            room.name = name
            room.capacity = capacity
            room.projector = projector
            room.availability = availability
            room.save()
            return redirect('/rooms/')
        # commenting on incorrect filling of the form with data
        else:
            if not name:
                messages.error(request, "Room name not provided.")
            if capacity <= 0:
                messages.error(request, "Room capacity must be greater than 0.")

            return HttpResponseRedirect('/rooms/')

def rooms(request):

    if request.method == "POST":
        sort_option = request.POST.get('sort_option')
        if sort_option == '1':
            rooms = Rooms.objects.order_by('-capacity')
        elif sort_option == '2':
            rooms = Rooms.objects.order_by('capacity')
        else:
            #If the request is POST but no sort_option,
            # we redirect to the same view, but without sorting.
            return HttpResponseRedirect('/rooms/')

    else:
        rooms = Rooms.objects.all()

    if not rooms:
        return HttpResponse("No rooms available")

    context = {
        "rooms": rooms,
    }
    return render(request, "rooms.html", context)


def del_room(request, id):
    room = Rooms.objects.get(pk=id)
    if request.method == 'GET':
        room.delete()
        messages.success(request, "room removed")
        return redirect('/rooms/')

    context = {
        "Rooms": room
    }
    return render(request, "del_rooms.html", context)

def rezerv_room(request, id):
    room = Rooms.objects.get(pk=id)

    if request.method == 'GET':
        return render(request, 'rezerv_room.html', {'room': room})

    if request.method == "POST":
        comment = request.POST.get('comment')
        form_date = request.POST.get('date')

        # Verify that the room on the day is not already booked
        existing_reservation = Room_reservation.objects.filter(room=room, date=form_date).first()
        if existing_reservation:
            messages.error(request, "Sala jest już zarezerwowana na wybraną datę.")
            return render(request, 'rezerv_room.html', {'room': room})

        # Check that the given date is not in the past
        try:
            form_date = date.fromisoformat(form_date)
        except ValueError:
            messages.error(request, "Nieprawidłowy format daty.")
            return render(request, 'rezerv_room.html', {'room': room})

        dzisiejsza_data = date.today()
        if form_date < dzisiejsza_data:
            messages.error(request, "Data nie może być z przeszłości.")
            return render(request, 'rezerv_room.html', {'room': room})

        # Save room reservation
        reservation = Room_reservation(date=form_date, room=room, comment=comment)
        reservation.save()

        # Update availability to False (reserved room)
        room.availability = False
        room.save()

        messages.success(request, "Rezerwacja sali zakończona powodzeniem.")
        return redirect('/rooms/')

def detailed_view(request, id):
    room = Rooms.objects.get(pk=id)

    if request.method == "POST":
        sort_option = request.POST.get('sort_option')
        if sort_option == '1':
            reservation = Room_reservation.objects.filter(room=room).order_by('date')
        elif sort_option == '2':
            reservation = Room_reservation.objects.filter(room=room).order_by('-date')
    else:
        reservation = Room_reservation.objects.filter(room=room).order_by('date')


    context = {
        "room": room,
        "reservation": reservation
    }
    return render(request, "detailed_view.html", context)

def search_room(request):
    if request.method == "POST":
        name = request.POST.get('name')
        projector = request.POST.get('projector')
        capacity_from = request.POST.get('capacity_from')
        capacity_to = request.POST.get('capacity_to')
        availability_from = request.POST.get('availability_from')
        availability_to = request.POST.get('availability_to')  # New field for availability date range

        # Room search logic based on entered data

        # Download all rooms
        rooms = Rooms.objects.all()
        any_filter_applied = False  # Initialize flag to track if any filter is applied

        if name:
            rooms = rooms.filter(name__icontains=name)
            any_filter_applied = True

        if projector == 'True':
            rooms = rooms.filter(projector=True)
            any_filter_applied = True
        elif projector == 'False':
            rooms = rooms.filter(projector=False)
            any_filter_applied = True

        if capacity_from and capacity_to:
            rooms = rooms.filter(capacity__range=(capacity_from, capacity_to))
            any_filter_applied = True

        if availability_from and availability_to:
            # Convert availability dates to date objects
            availability_from = date.fromisoformat(availability_from)
            # use the date.fromisoformat() function to convert the entered dates (which are in ISO format)
            # into Python date objects. This allows us to operate on these dates in our database query.
            availability_to = date.fromisoformat(availability_to)
            rooms = rooms.filter(room_reservation__date__range=(availability_from, availability_to))
            any_filter_applied = True

        if not any_filter_applied:
            messages.info(request, "Please enter search criteria.")
            return render(request, "search_room.html")
        # Check if any rooms were found
        if not rooms.exists():
            messages.info(request, "No rooms found matching the search criteria.")

        context = {
            "rooms": rooms
        }
        return render(request, "search_room.html", context)
    else:
        return render(request, "search_room.html")

