from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from django.http import Http404, HttpResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse_lazy
from django.views import View

from .forms import SignUpForm, TransactionForm
from .models import LottoBought, Room, Round, Transaction


def signup_method(request):
    template_name = 'signup.html'
    success_url=reverse_lazy('lotto:main')
    if request.user.is_anonymous:
        if request.method == "POST":
            form = SignUpForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                form.save()
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect(success_url)
            else:
                errors = form.errors.items()
                form = SignUpForm()
                context = {
                    'form': form, 'errors' : errors
                }
                return render(request, template_name, context)
    else:
        return redirect(success_url)
    form = SignUpForm()
    context = {
        'form': form
    }
    return render(request, template_name, context)

def login_method(request):
    template_name = 'login.html'
    success_url=reverse_lazy('lotto:main')
    if request.user.is_anonymous:
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect(success_url)
    else:
        return redirect(success_url)
    form = AuthenticationForm()
    context = {
        "form": form
    }
    return render(request, template_name, context)

class MainView(View):
    template_name = 'main.html'
    def get(self, request):
        ctx = {}
        return render(request, self.template_name, ctx)
    
class RoomView(View):
    template_name = 'rooms.html'
    def get(self, request):
        round_latest = Round.objects.latest('id')
        room1 = Room.objects.get(id=1)
        lottos_1 = room1.transactions.filter(round_bought=round_latest).values_list('lotto', flat=True)
        room2 = Room.objects.get(id=2)
        lottos_2 = room2.transactions.filter(round_bought=round_latest).values_list('lotto', flat=True)
        room3 = Room.objects.get(id=3)
        lottos_3 = room3.transactions.filter(round_bought=round_latest).values_list('lotto', flat=True)
        room4 = Room.objects.get(id=4)
        lottos_4 = room4.transactions.filter(round_bought=round_latest).values_list('lotto', flat=True)
        room5 = Room.objects.get(id=5)
        lottos_5 = room5.transactions.filter(round_bought=round_latest).values_list('lotto', flat=True)
        room_lottos = [
            {"room": 1, "lottos": lottos_1},
            {"room": 2, "lottos": lottos_2},
            {"room": 3, "lottos": lottos_3},
            {"room": 4, "lottos": lottos_4},
            {"room": 5, "lottos": lottos_5},
        ]
        ctx = {
            "room_lottos": room_lottos
        }
        return render(request, self.template_name, ctx)

class BuyLottoView(View):
    template_name = 'buy_lotto.html'
    success_url=reverse_lazy('lotto:main')
    def get(self, request, room, error = ""):
        if request.user.is_authenticated:
            round_latest = Round.objects.latest('id')
            shares = get_shares_room(room)
            disabled = True if shares == 50 else False
            bought_lottos = request.user.transactions.filter(room = room, round_bought=round_latest).values_list('lotto', flat=True)
            pending_transactions = get_pending_lottos(room)
            successful_transactions = get_successful_lottos(room)
            ctx = {
                "room": room,
                "round": round_latest,
                "shares": shares,
                "disabled": disabled,
                "successful_transactions": successful_transactions,
                "pending_transactions": pending_transactions,
                "bought_lottos": bought_lottos,
                "error": error
            }
            return render(request, self.template_name, ctx)
        else:
            return redirect(self.success_url)
    
class ConfirmBuyLottoView(View):
    template_name = 'confirm_buy_lotto.html'
    success_url=reverse_lazy('lotto:transactions')
    home = reverse_lazy('lotto:main')
    def get(self, request, room):
        if request.user.is_authenticated:
            sixth = request.GET.get("sixth")
            fifth = request.GET.get("fifth")
            fourth = request.GET.get("fourth")
            share = request.GET.get("share")
            round_latest = Round.objects.latest('id')
            lotto = fourth+fifth+sixth
            shares_room = get_shares_room(room) if get_shares_room(room) is not None else 0
            shares_lotto = get_shares_lotto(lotto) if get_shares_lotto(lotto) is not None else 0
            # ในห้องจะต้องไม่เกิน 50
            check_shares_room = (int(share)+shares_room > 50)
            # เลขนี้ในทุกห้องต้องไม่เกิน 50
            check_shares_lotto = (int(share)+shares_lotto > 50)
            pool = request.user.transactions.filter(round_bought=round_latest, room = room).values_list('lotto', flat=True)
            if lotto in pool or check_shares_room or check_shares_lotto:
                # return redirect(reverse_lazy("lotto:buy_lotto", kwargs={'error': lotto+" is already bought."}))
                # return redirect(reverse_lazy("lotto:buy_lotto", kwargs={'room': room}))
                return BuyLottoView.get(request=request, room=room, error= lotto+" is already bought in this round.")
            else:
                ctx = {
                    "room": room,
                    "round": round_latest,
                    "lotto": lotto,
                    "share": share,
                    "total": int(share)*80,
                }
                return render(request, self.template_name, ctx)
        else:
            return redirect(self.home)
    
    def post(self, request, room):
        if request.user.is_authenticated:
            user = request.user
            room_in = Room.objects.get(id = room)
            round_latest = Round.objects.latest('id')
            lotto = request.POST.get("lotto")
            share = request.POST.get("share")
            if (user and lotto and share):
                transaction = Transaction(user=user, lotto=lotto, share=share, room = room_in, round_bought = round_latest)
                transaction.save()
                room_in.shares += 1
                room_in.save()
                return redirect(self.success_url)
            else:
                errors = ["Required inputs are not filled"]
                ctx = {
                    "errors": errors
                }
                return render(request, self.template_name, ctx)
        else:
            return redirect(self.home)
    
class TransactionView(View):
    template_name = 'transactions.html'
    success_url=reverse_lazy('lotto:transactions')
    home=reverse_lazy('lotto:main')
    def get(self, request):
        round_latest = Round.objects.latest('id')
        if request.user.is_superuser:
            old_transactions = Transaction.objects.exclude(round_bought=round_latest)
            pending_transactions = Transaction.objects.filter(status="รอการยืนยันการชำระเงิน", round_bought=round_latest) | Transaction.objects.filter(status="การชำระเงินไม่สำเร็จ", round_bought=round_latest)
            successful_transactions = Transaction.objects.filter(status="คำสั่งซื้อสำเร็จ", round_bought=round_latest)
            ctx = {
                "old_transactions": old_transactions,
                "pending_transactions": pending_transactions,
                "successful_transactions": successful_transactions
            }
            return render(request, self.template_name, ctx)
        elif request.user.is_authenticated:
            old_transactions = request.user.transactions.exclude(round_bought=round_latest)
            pending_transactions = request.user.transactions.filter(status="รอการยืนยันการชำระเงิน", round_bought=round_latest) | request.user.transactions.filter(status="การชำระเงินไม่สำเร็จ", round_bought=round_latest)
            successful_transactions = request.user.transactions.filter(status="คำสั่งซื้อสำเร็จ", round_bought=round_latest)
            ctx = {
                "old_transactions": old_transactions,
                "pending_transactions": pending_transactions,
                "successful_transactions": successful_transactions
            }
            return render(request, self.template_name, ctx)
        else:
            return redirect(self.home)
        
    def post(self, request, pk):
        if request.user.is_superuser:
            flush = request.POST.get("flush")
            round_latest = Round.objects.latest('id')
            if flush:
                # new round
                round_new = Round(date="2024:12:16")
                round_new.save()
                rooms = Room.objects.all()
                for room in rooms:
                    room.shares = 0
                    room.save()
            else:
                transaction = get_object_or_404(Transaction, id=pk)
                response = request.POST.get("response")
                if response == "1":
                    transaction.status = "คำสั่งซื้อสำเร็จ"
                    transaction.save()
                else:
                    transaction.status = "การชำระเงินไม่สำเร็จ"
                    transaction.save()
            return redirect(self.success_url)
        else:
            return redirect(self.home)

class StatView(View):
    template_name = 'lotto_stat.html'
    success_url=reverse_lazy('lotto:main')
    def get(self, request, mode = 2, query = False):
        stats = []
        sixth = request.GET.get("sixth")
        fifth = request.GET.get("fifth")
        fourth = request.GET.get("fourth")
        third = request.GET.get("third")
        second = request.GET.get("second")
        first = request.GET.get("first")
        if(mode == 2 and sixth and fifth):
            query = True
            lotto = str(fifth) + str(sixth)
            stats = get_stats(lotto)
        elif(mode == 3 and sixth and fifth and fourth):
            query = True
            lotto = str(fourth) + str(fifth) + str(sixth)
            stats = get_stats(lotto)
        elif(mode == 5 and sixth and fifth and fourth and third and second):
            query = True
            lotto = str(second) + str(third) + str(fourth) + str(fifth) + str(sixth)
            stats = get_stats(lotto)
        elif(mode == 6 and sixth and fifth and fourth and third and second and first):
            query = True
            lotto = str(first) + str(second) + str(third) + str(fourth) + str(fifth) + str(sixth)
            stats = get_stats(lotto)
        ctx = {
            "mode": mode,
            "stats": stats,
            "query": query,
            "sixth": sixth,
            "fifth": fifth,
            "fourth": fourth,
            "third": third,
            "second": second,
            "first": first
        }
        return render(request, self.template_name, ctx)

def get_stats(lotto):
    with connection.cursor() as cursor:
        cursor.execute(" CALL getLottoStats(%s)", (lotto,))
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"type": row[0], "count": row[1]} for row in result]
    return stats

def get_pending_lottos(room):
    with connection.cursor() as cursor:
        cursor.execute(" CALL getPendingLottos(%s)", (room,))
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats

def get_successful_lottos(room):
    with connection.cursor() as cursor:
        cursor.execute(" CALL getSuccessfulLottos(%s)", (room,))
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats

def get_shares_room(room):
    with connection.cursor() as cursor:
        cursor.execute("CALL transRoomSum(%s)", (room,))
        result = cursor.fetchone()
    return result[0]

def get_shares_lotto(lotto):
    with connection.cursor() as cursor:
        cursor.execute("CALL transLottoSum(%s)", (lotto,))
        result = cursor.fetchone()
    return result[0]
