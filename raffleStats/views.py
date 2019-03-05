from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Raffle

def index(request):
    raffles = Raffle.objects.order_by('-datetime_completed')
    context = {'raffles': raffles}
    return render(request, 'raffleStats/index.html', context)

# Create your views here.
