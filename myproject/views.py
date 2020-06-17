from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def homeindex(request):
    return render(request, 'myproject/index.html')

def about_me(request):
    return render(request, 'myproject/about.html')
