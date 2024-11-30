from django.shortcuts import render
from django.views import View


class MainView(View):
    template_name = 'main.html'
    def get(self, request, mode = 2):
        result = ""
        sixth = request.GET.get("sixth")
        fifth = request.GET.get("fifth")
        fourth = request.GET.get("fourth")
        third = request.GET.get("third")
        second = request.GET.get("second")
        first = request.GET.get("first")
        if(mode == 2 and sixth and fifth):
            result="2ja"
            # use query statement to trigger programable object
        elif(mode == 3 and sixth and fifth and fourth):
            result="3ja"
            # use query statement to trigger programable object
        elif(mode == 6 and sixth and fifth and fourth and third and second and first):
            result="6ja"
            # use query statement to trigger programable object
        ctx = {
            "mode": mode,
            "result": result,
            "sixth": sixth,
            "fifth": fifth,
            "fourth": fourth,
            "third": third,
            "second": second,
            "first": first
        }
        return render(request, self.template_name, ctx)

