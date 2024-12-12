<<<<<<< HEAD
from django.urls import path
=======
from django.urls import path, include
from django.contrib import admin
>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d

from . import views

app_name='lotto'
urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path("stat", views.StatView.as_view(), name="stat"),
    path("stat/<int:mode>", views.StatView.as_view(), name="stat_mode"),
<<<<<<< HEAD
    path("stattable", views.StatViewTable.as_view(), name="stattable"),
    path('table', views.StatViewTable.as_view(), name='table'),
    path('table/<int:mode>', views.StatViewTable.as_view(), name='table_mode'),

    path("buy", views.BuyLottoView.as_view(), name="buy_lotto"),
    path("buy/confirm", views.ConfirmBuyLottoView.as_view(), name="confirm_buy_lotto"),
    path("buy/<str:error>", views.BuyLottoView.as_view(), name="buy_lotto"),
    path("transactions/", views.TransactionView.as_view(), name="transactions"),
    path("transactions/<int:pk>", views.TransactionView.as_view(), name="transactions"),
    
    path("signup/", views.signup_method, name="signup"),
    path("login/", views.login_method, name="login"),
=======
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path('logout/', views.userlogout, name='logout'), 
    path('profile/', views.profile, name='profile'),
>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d
]