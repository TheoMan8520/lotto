from django.urls import path

from . import views

app_name='lotto'
urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path("stat", views.StatView.as_view(), name="stat"),
    path("stat/<int:mode>", views.StatView.as_view(), name="stat_mode"),
    
    path("buy", views.BuyLottoView.as_view(), name="buy_lotto"),
    path("buy/confirm", views.ConfirmBuyLottoView.as_view(), name="confirm_buy_lotto"),
    path("transactions/", views.TransactionView.as_view(), name="transactions"),
    
    path("signup/", views.signup_method, name="signup"),
    path("login/", views.login_method, name="login"),
]