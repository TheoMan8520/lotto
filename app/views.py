<<<<<<< HEAD
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from django.http import Http404, HttpResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse_lazy
from django.views import View

from .forms import SignUpForm, TransactionForm
from .models import Transaction
from .models import Account


def signup_method(request):
    template_name = 'signup.html'
    success_url=reverse_lazy('lotto:main')
    if request.user.is_anonymous:
        if request.method == "POST":
            form = SignUpForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                first_name = form.cleaned_data.get('firs_tname')
                last_name = form.cleaned_data.get('last_name')
                banknumber = form.cleaned_data.get('banknumber')
                bankname = form.cleaned_data.get('bankname')

                user = form.save()

                Account.objects.create(user=user, banknumber=banknumber, bankname=bankname)

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
    success_url = reverse_lazy('lotto:main')
    errors = [] 

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
                    errors.append("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            else:
                errors.append("เข้าสู่ระบบไม่สำเร็จ")
    else:
        return redirect(success_url)

    form = AuthenticationForm()
    context = {
        "form": form,
        "errors": errors 
    }
    return render(request, template_name, context)

class MainView(View):
    template_name = 'main.html'
=======
from django.db import connection
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

class MainView(View):
    template_name = 'main.html'

>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d
    def get(self, request):
        ctx = {}
        return render(request, self.template_name, ctx)
    
<<<<<<< HEAD

    
class BuyLottoView(View):
    template_name = 'buy_lotto.html'
    success_url=reverse_lazy('lotto:main')
    def get(self, request, error = ""):
        if request.user.is_authenticated:
            bought_lottos = request.user.transactions.all().values_list('lotto', flat=True)
            successful_transactions = get_successful_lottos()
            pending_transactions = get_pending_lottos()
            ctx = {
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
    def get(self, request):
        if request.user.is_authenticated:
            sixth = request.GET.get("sixth")
            fifth = request.GET.get("fifth")
            fourth = request.GET.get("fourth")
            share = request.GET.get("share")
            lotto = fourth+fifth+sixth
            pool = request.user.transactions.all().values_list('lotto', flat=True)
            if lotto in pool:
                return redirect(reverse_lazy("lotto:buy_lotto", kwargs={'error': lotto+" is already bought."}))
            else:
                ctx = {
                    "lotto": lotto,
                    "share": share,
                    "total": int(share)*80
                }
                return render(request, self.template_name, ctx)
        else:
            return redirect(self.home)
    
    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            lotto = request.POST.get("lotto")
            share = request.POST.get("share")
            if (user and lotto and share):
                transaction = Transaction(user=user, lotto=lotto, share=share)
                transaction.save()
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
        if request.user.is_superuser:
            # transactions = Transaction.objects.all()
            pending_transactions = Transaction.objects.filter(status="รอการยืนยันการชำระเงิน")
            successful_transactions = Transaction.objects.filter(status="คำสั่งซื้อสำเร็จ")
            ctx = {
                # "transactions": transactions
                "pending_transactions": pending_transactions,
                "successful_transactions": successful_transactions
            }
            return render(request, self.template_name, ctx)
        elif request.user.is_authenticated:
            pending_transactions = request.user.transactions.filter(status="รอการยืนยันการชำระเงิน")
            successful_transactions = request.user.transactions.filter(status="คำสั่งซื้อสำเร็จ")
            # transactions = request.user.transactions.all()
            ctx = {
                # "transactions": transactions
                "pending_transactions": pending_transactions,
                "successful_transactions": successful_transactions
            }
            return render(request, self.template_name, ctx)
        else:
            return redirect(self.home)
    def post(self, request, pk):
        if request.user.is_superuser:
            transaction = get_object_or_404(Transaction, id=pk)
            transaction.status = "คำสั่งซื้อสำเร็จ"
            transaction.save()
            return redirect(self.success_url)
        else:
            return redirect(self.home)

class StatView(View):
    template_name = 'lotto_stat.html'
    success_url = reverse_lazy('lotto:main')

    def get(self, request, mode=2, query=False):
        stats = []
        stats2 = []
        a = None 
        
        sixth = request.GET.get("sixth")
        fifth = request.GET.get("fifth")
        fourth = request.GET.get("fourth")
      

        if mode == 2 and sixth and fifth:
            query = True
            lotto = str(fifth) + str(sixth)
            stats, a = get_stats(lotto) 
            
        elif mode == 3 and sixth and fifth and fourth:
            query = True
            lotto = str(fourth) + str(fifth) + str(sixth)
            stats, a = get_stats(lotto) 

        ctx = {
            "mode": mode,
            "stats": stats,
            "stats2": stats2,
=======
class StatView(View):
    template_name = 'lotto_stat.html'
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
>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d
            "query": query,
            "sixth": sixth,
            "fifth": fifth,
            "fourth": fourth,
<<<<<<< HEAD
            "percentage": a,
=======
            "third": third,
            "second": second,
            "first": first
>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d
        }
        return render(request, self.template_name, ctx)

def get_stats(lotto):
    with connection.cursor() as cursor:
<<<<<<< HEAD
        cursor.execute("CALL getLottoStats(%s)", (lotto,))
        result = cursor.fetchall()
    stats = [{"type": row[0], "count": row[1]} for row in result]
    total_count = sum(row[1] for row in result) 
    percentage = round((total_count / 1195) * 100, 3) if total_count else 0 
    return stats, percentage



def get_pending_lottos():
    with connection.cursor() as cursor:
        cursor.execute(" CALL getPendingLottos()")
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats

def get_successful_lottos():
    with connection.cursor() as cursor:
        cursor.execute(" CALL getSuccessfulLottos()")
        result = cursor.fetchall()
    # result alone card rebel
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats


def get_stats_table(type):
    with connection.cursor() as cursor:
        cursor.execute(" CALL getLottoStatsTable(%s)", (type,))
        result = cursor.fetchall()
    stats = [{"lotto": row[0], "count": row[1]} for row in result]
    return stats

class StatViewTable(View):
    template_name = 'stattable.html'
    def get(self, request, mode = 2, query = False):
        stats2 = []
        stats3= []
        stats2 = get_stats_table("prize_2digits")
        if(mode == 2):
            query = True
            stats2 = get_stats_table("prize_2digits")
           
        elif(mode == 3 ):
            query = True
            stats2 = get_stats_table("prize_pre_3digits")
            stats3 = get_stats_table("prize_sub_3digits")
        ctx = {
            "mode": mode,
            "stats2": stats2,
            "stats3": stats3,
        }
        return render(request, self.template_name, ctx)
=======
        cursor.execute(" CALL getLottoStats(%s)", (lotto,))
        result = cursor.fetchall()
    stats = [{"type": row[0], "count": row[1]} for row in result]
    return stats



def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"User {user.username} registered successfully.") 
            auth_login(request, user)
            messages.success(request, f"Registration successful!")
            return redirect('lotto:login')
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  
            return redirect('lotto:main') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def userlogout(request):
    logout(request)
    return redirect(reverse('lotto:main'))

@login_required
def profile(request):
    return render(request, 'profile.html')
>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d
