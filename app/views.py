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

    def get(self, request):
        ctx = {}
        return render(request, self.template_name, ctx)
    
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