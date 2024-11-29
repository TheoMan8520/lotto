from django.shortcuts import render
from django.views import View


class MainView(View):
    template_name = 'main.html'
    def get(self, request):
        ctx = {}
        return render(request, self.template_name, ctx)
