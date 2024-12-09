from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from django.http import Http404, HttpResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse_lazy
from django.views import View

from .forms import SignUpForm, TransactionForm
from .models import Transaction


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
    
class BuyLottoView(View):
    template_name = 'buy_lotto.html'
    success_url=reverse_lazy('lotto:main')
    def get(self, request):
        if request.user.is_authenticated:
            ctx = {}
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
            ctx = {
                "lotto": fourth+fifth+sixth,
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
            transactions = Transaction.objects.all()
            ctx = {
                "transactions": transactions
            }
            return render(request, self.template_name, ctx)
        elif request.user.is_authenticated:
            transactions = request.user.transactions.all()
            ctx = {
                "transactions": transactions
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
    stats = [{"type": row[0], "count": row[1]} for row in result]
    return stats