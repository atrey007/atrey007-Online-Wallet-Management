from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import UserProfile
from django.conf import settings
import razorpay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from decimal import Decimal
from django.http import HttpResponseBadRequest

# Registration view
@login_required
def add_money(request):
    return render(request, 'wallet/add_money.html')
def home(request):
    return render(request, 'wallet/home.html')  # Adjust the template path if needed
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            UserProfile.objects.create(user=user, balance=0)
            auth_login(request, user)  # Log in the user after registration
            return redirect('wallet:balance')
    else:
        form = RegisterForm()
    return render(request, 'wallet/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('wallet:balance_view')
    else:
        form = LoginForm()
    return render(request, 'wallet/login.html', {'form': form})

# View for checking balance
@login_required
def balance_view(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'wallet/balance.html', {'balance': profile.balance})

# Add money via Razorpay
# wallet/views.py



    
    return render(request, 'wallet/add_money_razorpay.html', context)
@csrf_exempt  # Exempt CSRF for Razorpay's POST request
# wallet/views.py

@login_required
def add_money_razorpay(request):
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 0))  # Get the amount in INR

        # Ensure the amount is at least ₹1
        if amount < 1:
            return HttpResponseBadRequest("The minimum amount allowed is ₹1.")

        amount_in_paise = amount * 100  # Convert INR to paise for Razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({
            'amount': amount_in_paise,  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'
        })

        return render(request, 'wallet/add_money_razorpay.html', {
            'payment': payment,
            'amount': amount  # Pass the amount in INR for display
        })

    return render(request, 'wallet/add_money.html')

@login_required
def payment_success(request):
    payment_id = request.POST.get('payment_id')
    order_id = request.POST.get('order_id')
    signature = request.POST.get('signature')
    
    # Verify payment signature
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        })
    except razorpay.errors.SignatureVerificationError:
        return HttpResponseBadRequest('Invalid signature.')

    # Get the user profile and update balance
    profile = UserProfile.objects.get(user=request.user)
    amount = float(request.POST.get('amount', 0)) / 100  # Convert paise to INR
    profile.balance += amount
    profile.save()

    # Redirect to the add_money page with updated balance
    return redirect('wallet:balance_view')

    