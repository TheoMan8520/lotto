from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from django.http import Http404, HttpResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse_lazy
from django.views import View

from .forms import SignUpForm, TransactionForm
from .models import Account, LottoBought, Room, Round, Slip, Transaction


def signup_method(request):
    template_name = 'signup.html'
    success_url=reverse_lazy('lotto:main')
    if request.user.is_anonymous:
        if request.method == "POST":
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                
                banknumber = form.cleaned_data.get('banknumber')
                bankname = form.cleaned_data.get('bankname')
                Account.objects.create(user=user, banknumber=banknumber, bankname=bankname)
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
    
class RoomsView(View):
    template_name = 'rooms.html'
    def get(self, request):
        round_latest = get_latest_round()
        lottos_1 = get_lottos_room(round_latest.id, 1)
        lottos_2 = get_lottos_room(round_latest.id, 2)
        lottos_3 = get_lottos_room(round_latest.id, 3)
        lottos_4 = get_lottos_room(round_latest.id, 4)
        lottos_5 = get_lottos_room(round_latest.id, 5)
        room_lottos = [
            {"room": 1, "lottos": lottos_1},
            {"room": 2, "lottos": lottos_2},
            {"room": 3, "lottos": lottos_3},
            {"room": 4, "lottos": lottos_4},
            {"room": 5, "lottos": lottos_5},
        ]
        ctx = {
            "room_lottos": room_lottos,
            "round": round_latest
        }
        return render(request, self.template_name, ctx)

class RoomView(View):
    template_name = 'room_detail.html'
    def get(self, request, room):
        room_in = Room.objects.get(id = room)
        round_latest = get_latest_round()
        lottos_bought = room_in.lottos.filter(round_bought = round_latest)
        total = get_total_prize(round_latest.id, room)
        shares_own = 0
        shares_percent = 0
        shares_total = 0
        if(lottos_bought):
            shares_own = get_shares_own(request.user.id, round_latest.id, room)
            shares_percent = (shares_own / room_in.shares) * 100
            shares_total = float(shares_percent) * float(total) / 100
        bought_lottos = get_bought_lottos(request.user.id, round_latest.id, room)
        pending_transactions = get_pending_lottos(round_latest.id, room)
        successful_transactions = get_successful_lottos(round_latest.id, room)
        ctx = {
            "room": room_in,
            "round": round_latest,
            "lottos_bought": lottos_bought,
            "total": total,
            "shares_own": shares_own,
            "shares_percent": round(shares_percent, 2),
            "shares_total": round(shares_total, 2),
            "successful_transactions": successful_transactions,
            "pending_transactions": pending_transactions,
            "bought_lottos": bought_lottos,
        }
        return render(request, self.template_name, ctx)
    
class RoomHistoryView(View):
    template_name = 'room_detail.html'
    def get(self, request, room, round_id):
        room_in = Room.objects.get(id = room)
        round_in = Round.objects.get(id=round_id)
        lottos_bought = room_in.lottos.filter(round_bought = round_in)
        total = get_total_prize(round_id, room)
        shares_own = 0
        shares_percent = 0
        shares_total = 0
        if(lottos_bought):
            shares_own = get_shares_own(request.user.id, round_id, room)
            # shares ทั้งหมดในห้อง
            shares_percent = (shares_own / get_shares_room(round_id, room)) * 100
            shares_total = shares_percent * total / 100
        bought_lottos = get_bought_lottos(request.user.id, round_id, room)
        pending_transactions = get_pending_lottos(round_id, room)
        successful_transactions = get_successful_lottos(round_id, room)
        ctx = {
            "room": room_in,
            "round": round_in,
            "disabled": True,
            "lottos_bought": lottos_bought,
            "total": total,
            "shares_own": shares_own,
            "shares_percent": round(shares_percent, 2),
            "shares_total": round(shares_total, 2),
            "successful_transactions": successful_transactions,
            "pending_transactions": pending_transactions,
            "bought_lottos": bought_lottos,
        }
        return render(request, self.template_name, ctx)

class BuyLottoView(View):
    template_name = 'buy_lotto.html'
    success_url=reverse_lazy('lotto:main')
    def get(self, request, room, error = []):
        if request.user.is_authenticated:
            round_latest = get_latest_round()
            shares = get_shares_room(get_latest_round().id, room)
            disabled = True if shares == 50 else False
            bought_lottos = get_bought_lottos(request.user.id, round_latest.id, room)
            pending_transactions = get_pending_lottos(round_latest.id, room)
            successful_transactions = get_successful_lottos(round_latest.id, room)
            ctx = {
                "room": room,
                "round": round_latest,
                "shares": shares,
                "disabled": disabled,
                "successful_transactions": successful_transactions,
                "pending_transactions": pending_transactions,
                "bought_lottos": bought_lottos,
                "errors": error
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
            round_latest = get_latest_round()
            lotto = fourth+fifth+sixth
            shares_own = get_shares_own(request.user.id, round_latest.id, room)
            shares_room = get_shares_room(round_latest.id, room) 
            shares_lotto = get_shares_lotto(lotto) 
            # ในห้องจะต้องไม่เกิน 50
            check_shares_room = (int(share)+shares_room > 50)
            # เลขนี้ในทุกห้องต้องไม่เกิน 50
            check_shares_lotto = (int(share)+shares_lotto > 50)
            check_shares_own = shares_own+int(share) > 10
            pool = get_bought_lottos(request.user.id, round_latest.id, room)
            err_mes = []
            if(lotto in pool): err_mes.append(lotto+" is already bought in this room. You can neither change or buy this lotto again.")
            if(check_shares_room): err_mes.append("Room's shares exceed limit. Only %d shares left for this room." %(50-shares_room))
            if(check_shares_lotto): err_mes.append("Lotto's shares exceed limit. Only %d shares left for this lotto." %(50-shares_room))
            if(check_shares_own): err_mes.append("You buy exceeding shares. Only %d shares left for you in this room." %(10-shares_own))
            if len(err_mes) > 0:
                return BuyLottoView.get(BuyLottoView, request=request, room=room, error= err_mes)
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
            round_latest = get_latest_round()
            lotto = request.POST.get("lotto")
            share = request.POST.get("share")
            if (user and lotto and share):
                transaction = Transaction(user=user, lotto=lotto, share=share, room = room_in, round_bought = round_latest)
                transaction.save()
                room_in.shares += int(share)
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

class SlipsView(View):
    template_name = 'slips.html'
    success_url=reverse_lazy('lotto:slips')
    def get(self, request):
        if(request.user.is_superuser):
            pending_slips = get_pending_slips()
            successful_slips = get_success_slips()
            ctx = {
                "pending_slips": pending_slips,
                "successful_slips": successful_slips
            }
            return render(request, self.template_name, ctx)
        elif request.user.is_authenticated:
            pending_slips = get_pending_slips_user(request.user)
            successful_slips = get_success_slips_user(request.user)
            ctx = {
                "pending_slips": pending_slips,
                "successful_slips": successful_slips
            }
            return render(request, self.template_name, ctx)

    def post(self, request, pk):
        if(request.user.is_superuser):
            slip = Slip.objects.get(id=pk)
            slip.status = "ดำเนินการสำเร็จ"
            slip.save()
            return redirect(self.success_url)

class TransactionView(View):
    template_name = 'transactions.html'
    success_url=reverse_lazy('lotto:transactions')
    home=reverse_lazy('lotto:main')
    def get(self, request):
        round_latest = get_latest_round()
        if request.user.is_superuser:
            old_transactions = Transaction.objects.exclude(round_bought=round_latest)
            pending_transactions = get_pending_transactions()
            successful_transactions = get_success_transactions()
            ctx = {
                "old_transactions": old_transactions,
                "pending_transactions": pending_transactions,
                "successful_transactions": successful_transactions
            }
            return render(request, self.template_name, ctx)
        elif request.user.is_authenticated:
            old_transactions = request.user.transactions.exclude(round_bought=round_latest)
            pending_transactions = get_pending_transactions_user(request.user)
            successful_transactions = get_success_transactions_user(request.user)
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
            re_round = request.POST.get("reround")
            close_round = request.POST.get("closeround")
            if close_round:
                rooms = Room.objects.all()
                for room in rooms:
                    room.is_open = False
                    room.save()
            elif re_round:
                reround()
            else:
                transaction = get_object_or_404(Transaction, id=pk)
                response = request.POST.get("response")
                if response == "1":
                    transaction.status = "คำสั่งซื้อสำเร็จ"
                    transaction.save()
                elif response == "0":
                    transaction.status = "การชำระเงินไม่สำเร็จ"
                    transaction.save()
                elif response == "2":
                    transaction.delete()
            return redirect(self.success_url)
        else:
            return redirect(self.home)

class StatView(View):
    template_name = 'lotto_stat.html'
    success_url=reverse_lazy('lotto:main')
    def get(self, request, mode = 2, query = False):
        stats = []
        stats2 = get_stats_table("prize_2digits")
        stats3_pre = get_stats_table("prize_pre_3digits")
        stats3_post = get_stats_table("prize_sub_3digits")
        stats_all = []
        sixth = request.GET.get("sixth")
        fifth = request.GET.get("fifth")
        fourth = request.GET.get("fourth")
        third = request.GET.get("third")
        second = request.GET.get("second")
        first = request.GET.get("first")

        if(mode == 2):
            stats_all = [
                {"mode": "เลขท้าย 2 ตัว", "stats": stats2}
            ]
        elif(mode == 3):
            stats_all = [
                {"mode": "เลขท้าย 3 ตัว", "stats": stats3_post},
                {"mode": "เลขหน้า 3 ตัว", "stats": stats3_pre},
            ]

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
            "stats_all": stats_all,
            "query": query,
            "sixth": sixth,
            "fifth": fifth,
            "fourth": fourth,
            "third": third,
            "second": second,
            "first": first,
        }
        return render(request, self.template_name, ctx)

def reround():
    # create slips for every user in every room
    round_latest = get_latest_round()
    rooms = Room.objects.all()
    for room in rooms:
        users_id = get_users_room(round_latest.id, room.id)
        total_prize = get_total_prize(round_latest.id, room.id)
        if total_prize:
            for user_id in users_id:
                user = get_user_model().objects.get(id=user_id)
                shares_own = get_shares_own(user.id, round_latest.id, room.id)
                shares_percent = (shares_own / get_shares_room(round_latest.id, room.id)) * 100
                shares_prize = shares_percent * total_prize / 100
                slip = Slip(prize = shares_prize, user=user, round_bought = round_latest, room=room)
                slip.save()
        # set share
        room.shares = 0
        room.is_open = True
        room.save()
        
    # new round
    day = round_latest.date.day
    month = round_latest.date.month
    year = round_latest.date.year
    if(day == 1):
        day = 16
    else:
        day = 1
        if(month < 12):
            month += 1
        else:
            month = 1
            year += 1
    date = str(year) + '-' + str(month) + '-' + str(day)
    round_new = Round(date=date)
    round_new.save()
    return None

def get_pending_slips():
    slips = Slip.objects.filter(status="กำลังดำเนินการ")
    return slips

def get_pending_slips_user(user):
    slips = Slip.objects.filter(status="กำลังดำเนินการ", user=user)
    return slips

def get_success_slips():
    slips = Slip.objects.filter(status="ดำเนินการสำเร็จ")
    return slips

def get_success_slips_user(user):
    slips = Slip.objects.filter(status="ดำเนินการสำเร็จ", user=user)
    return slips

def get_users_room(round_id, room):
    with connection.cursor() as cursor:
        cursor.execute("CALL getUsersRoom(%s, %s)", (round_id, room))
        result = cursor.fetchall()
    if result is not None:
        users = [row[0] for row in result]
        return users
    else:
        return []

def get_total_prize(round_id, room):
    with connection.cursor() as cursor:
        cursor.execute("CALL getTotalPrize(%s, %s)", (round_id, room))
        result = cursor.fetchone()
    if result[0] is not None:
        return result[0]
    else:
        return 0

def get_lottos_room(round_id, room):
    with connection.cursor() as cursor:
        cursor.execute("CALL getLottosRoom(%s, %s)", (round_id, room))
        result = cursor.fetchall()
    if result is not None:
        lottos = [row[0] for row in result]
        return lottos
    else:
        return []

def get_stats(lotto):
    with connection.cursor() as cursor:
        cursor.execute(" CALL getLottoStats(%s)", (lotto,))
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"type": row[0], "count": row[1]} for row in result]
    return stats

def get_stats_table(type):
    with connection.cursor() as cursor:
        cursor.execute(" CALL getLottoStatsTable(%s)", (type,))
        result = cursor.fetchall()
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats

def get_latest_round():
    return Round.objects.latest('id')

def get_pending_transactions():
    pending_transactions = Transaction.objects.filter(status="รอการยืนยันการชำระเงิน", round_bought=get_latest_round()) | Transaction.objects.filter(status="การชำระเงินไม่สำเร็จ", round_bought=get_latest_round())
    return pending_transactions
    # with connection.cursor() as cursor:
    #     cursor.execute("CALL getPendingTransactions()")
    #     rows = cursor.fetchall()
    #     columns = [col[0] for col in cursor.description]
    #     result = [dict(zip(columns, row)) for row in rows]
    # return result

def get_pending_transactions_user(uid):
    # rewrite without sql
    pending_transactions = Transaction.objects.filter(status="รอการยืนยันการชำระเงิน", round_bought=get_latest_round(), user=uid) | Transaction.objects.filter(status="การชำระเงินไม่สำเร็จ", round_bought=get_latest_round(), user=uid)
    return pending_transactions
    # with connection.cursor() as cursor:
    #     cursor.execute("CALL getPendingTransactionsUser(%s)", (uid,))
    #     rows = cursor.fetchall()
    #     columns = [col[0] for col in cursor.description]
    #     result = [dict(zip(columns, row)) for row in rows]
    # return result

def get_pending_lottos(round_id, room):
    with connection.cursor() as cursor:
        cursor.execute("CALL getPendingLottos(%s, %s)", (round_id, room,))
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats

def get_success_transactions():
    # rewrite without sql
    successful_transactions = Transaction.objects.filter(status="คำสั่งซื้อสำเร็จ", round_bought=get_latest_round())
    return successful_transactions
    # with connection.cursor() as cursor:
    #     cursor.execute("CALL getSuccessfulTransactions()")
    #     rows = cursor.fetchall()
    #     columns = [col[0] for col in cursor.description]
    #     result = [dict(zip(columns, row)) for row in rows]
    # return result

def get_success_transactions_user(uid):
    # rewrite without sql
    successful_transactions = Transaction.objects.filter(status="คำสั่งซื้อสำเร็จ", round_bought=get_latest_round(), user=uid)
    return successful_transactions
    # with connection.cursor() as cursor:
    #     cursor.execute("CALL getSuccessfulTransactionsUser(%s)", (uid,))
    #     rows = cursor.fetchall()
    #     columns = [col[0] for col in cursor.description]
    #     result = [dict(zip(columns, row)) for row in rows]
    # return result

def get_successful_lottos(round_id, room):
    with connection.cursor() as cursor:
        cursor.execute(" CALL getSuccessfulLottos(%s, %s)", (round_id, room,))
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats

def get_shares_room(round_id, room):
    with connection.cursor() as cursor:
        cursor.execute("CALL getSharesSumRoom(%s, %s)", (round_id, room,))
        result = cursor.fetchone()
    if result[0] is not None:
        return result[0]
    else:
        return 0

def get_shares_lotto(lotto):
    with connection.cursor() as cursor:
        cursor.execute("CALL getSharesSumLotto(%s)", (lotto,))
        result = cursor.fetchone()
    if result[0] is not None:
        return result[0]
    else:
        return 0

def get_shares_own(uid, round_id, room_id):
    with connection.cursor() as cursor:
        cursor.execute("CALL getShareOwn(%s, %s, %s)", (uid, round_id, room_id))
        result = cursor.fetchone()
    if result[0] is not None:
        return result[0]
    else:
        return 0

def get_bought_lottos(uid, round_id, room_id):
    with connection.cursor() as cursor:
        cursor.execute("CALL getBoughtLottos(%s, %s, %s)", (uid, round_id, room_id))
        result = cursor.fetchall()
    if result is not None:
        lottos = [row[0] for row in result]
        return lottos
    else:
        return []
