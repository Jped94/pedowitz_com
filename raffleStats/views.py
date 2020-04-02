from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Raffle, SpotCount
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

'''class RaffleHistoryView(ListView):
    model = Raffle
    paginate_by = 10
    context_object_name = 'raffles'
    template_name = 'index.html'
    ordering = ['datetime_completed']'''

def raffle_list(request):
    raffles = []
    raffles_full = Raffle.objects.order_by('-datetime_completed')
    page = request.GET.get('page', 1)
    paginator = Paginator(raffles_full, 20)

    try:
        raffles = paginator.page(page)
    except PageNotAnInteger:
        raffles = paginator.page(1)
    except EmptyPage:
        raffles = paginator.page(paginator.num_pages)

    context = {'raffles': raffles}
    return render(request, 'raffleStats/raffle_list.html', context)

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
