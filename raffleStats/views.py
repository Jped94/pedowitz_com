from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from .models import Raffle, SpotCount
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import DatasetDateForm
from django.urls import reverse
import datetime
import csv


def index(request):
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

    form = DatasetDateForm(request.POST or None)

    if request.method == 'POST':

        form = DatasetDateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/raffleStats/dataset/'
            + form.cleaned_data['from_date'].strftime('%d/%m/%Y')
            + "-"
            + form.cleaned_data['to_date'].strftime('%d/%m/%Y'))

    context = {'raffles': raffles, 'form': form}
    return render(request, 'raffleStats/index.html', context)

def history(request):
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
    return render(request, 'raffleStats/history.html', context)

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

def dataset_full(request):
    raffle_class = Raffle
    meta = raffle_class._meta
    field_names = [field.name for field in meta.fields]
    del field_names[-1] #remove URLs
    field_names.append('spot_histogram')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=RaffleStats_dataset.csv'
    writer = csv.writer(response)

def dataset(request, vfrom_date = None, vto_date = None):

    raffle_class = Raffle
    meta = raffle_class._meta
    field_names = [field.name for field in meta.fields]
    del field_names[-1] #remove URLs
    field_names.append('spot_histogram')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=RaffleStats_dataset.csv'
    writer = csv.writer(response)



    writer.writerow(field_names)
    del field_names[-1] #remove the spot histogram name again since its not in the raffle object

    if (vfrom_date != None and vto_date != None):
        from_date = datetime.datetime.strptime(vfrom_date, '%d/%m/%Y')
        to_date = datetime.datetime.strptime(vto_date, '%d/%m/%Y')
        for raffle in raffle_class.objects.filter(datetime_posted__range=[from_date, to_date]):
            row = [getattr(raffle, field) for field in field_names]
            row.append(raffle.get_spot_count_histogram())
            writer.writerow(row)
    else:
        for raffle in raffle_class.objects.order_by('-datetime_completed'):
            row = [getattr(raffle, field) for field in field_names]
            row.append(raffle.get_spot_count_histogram())
            writer.writerow(row)

    return response
