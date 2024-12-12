from django.urls import path

from . import views

app_name='lotto'
urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path("stat/", views.StatView.as_view(), name="stat"),
    path("stat/<int:mode>", views.StatView.as_view(), name="stat_mode"),
    
    path("room/<int:room>", views.RoomView.as_view(), name="room"),
    path("room/<int:room>/<int:round_id>", views.RoomHistoryView.as_view(), name="room_history"),
    path("rooms/", views.RoomsView.as_view(), name="rooms"),
    path("buy/<int:room>", views.BuyLottoView.as_view(), name="buy_lotto"),
    path("buy/confirm/<int:room>", views.ConfirmBuyLottoView.as_view(), name="confirm_buy_lotto"),
    path("slips/", views.SlipsView.as_view(), name="slips"),
    path("slips/<int:pk>", views.SlipsView.as_view(), name="slips"),
    path("transactions/", views.TransactionView.as_view(), name="transactions"),
    path("transactions/<int:pk>", views.TransactionView.as_view(), name="transactions"),
    
    path("signup/", views.signup_method, name="signup"),
    path("login/", views.login_method, name="login"),
]