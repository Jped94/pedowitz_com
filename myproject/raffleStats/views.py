from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("This is the raffle stats index")

# Create your views here.
