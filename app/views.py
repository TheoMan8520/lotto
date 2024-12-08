from django.db import connection
from django.shortcuts import render
from django.views import View


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