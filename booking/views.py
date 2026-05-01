import razorpay
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Hotel, Room, Booking
from django.conf import settings

# --- AUTHENTICATION VIEWS ---

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'register.html')

def user_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')


# --- MAIN VIEWS ---

def home(request):
    query = request.GET.get('q', '')
    if query:
        hotels = Hotel.objects.filter(location__icontains=query) | Hotel.objects.filter(name__icontains=query)
    else:
        hotels = Hotel.objects.all()
    return render(request, 'home.html', {'hotels': hotels, 'query': query})

def rooms(request, hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel)
    return render(request, 'rooms.html', {'hotel': hotel, 'rooms': rooms})


# --- BOOKING & PAYMENT VIEWS ---

@login_required
def book_room(request, room_id):
    room = Room.objects.get(id=room_id)
    
    if request.method == "POST":
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        # Prevent double booking
        existing = Booking.objects.filter(
            room=room,
            status='CONFIRMED',
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        if existing.exists():
            return HttpResponse("Room is already booked for these dates.")

        amount = room.price * 100  # Razorpay uses paise
        
        # Replace these with your actual keys for production
        razorpay_key = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_1DP5mmOlF5G5ag')
        razorpay_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'YOUR_SECRET')

        try:
            if razorpay_secret == 'YOUR_SECRET':
                raise Exception("Placeholder keys used.")
                
            client = razorpay.Client(auth=(razorpay_key, razorpay_secret))
            payment = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })
            payment_id = payment['id']
            is_simulation = False
        except Exception as e:
            # Fallback for interview/demo purposes if keys aren't set
            payment = {
                'id': f"order_demo_{room.id}_{request.user.id}",
                'amount': amount
            }
            payment_id = payment['id']
            is_simulation = True

        booking = Booking.objects.create(
            user=request.user,
            room=room,
            check_in=check_in,
            check_out=check_out,
            amount=room.price,
            razorpay_order_id=payment_id
        )

        return render(request, 'payment.html', {
            'payment': payment,
            'booking': booking,
            'razorpay_key': razorpay_key,
            'room': room,
            'is_simulation': is_simulation
        })
        
    return render(request, 'book.html', {'room': room})

@login_required
def payment_success(request):
    if request.method == "POST":
        order_id = request.POST.get('razorpay_order_id')
        
        if order_id:
            try:
                booking = Booking.objects.get(razorpay_order_id=order_id)
                booking.status = "CONFIRMED"
                booking.save()
            except Booking.DoesNotExist:
                pass

        return redirect('my_bookings')
    return redirect('home')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')
    return render(request, 'my_bookings.html', {'bookings': bookings})
