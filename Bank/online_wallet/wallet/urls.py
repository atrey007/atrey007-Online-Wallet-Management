# wallet/urls.py

from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('balance/', views.balance_view, name='balance_view'),
    path('add-money/', views.add_money, name='add_money'),
    path('add-money/razorpay/', views.add_money_razorpay, name='add_money_razorpay'),
     path('payment-success/', views.payment_success, name='payment_success'),
    # Add more URLs as needed
]
