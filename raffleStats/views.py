from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Raffle, SpotCount

def index(request):
    raffles = Raffle.objects.order_by('-datetime_completed')
    context = {'raffles': raffles}
    return render(request, 'raffleStats/index.html', context)

def details(request, vpost_id):
    spot_counts = SpotCount.objects.filter(post_id = vpost_id).order_by('num_spots')
    raffle = Raffle.objects.get(post_id = vpost_id)
    context = {'spot_counts': spot_counts, 'raffle':raffle}
    return render(request, 'raffleStats/details.html', context)

def spotcounts(request, vpost_id):
    spot_counts = SpotCount.objects.filter(post_id = vpost_id).order_by('num_spots')
    data = []
    for obj in spot_counts:
        entry = {
            'num_spots': obj.num_spots,
            'num_users': obj.count
        }
        data.append(entry)
    return JsonResponse(data, safe=False)
