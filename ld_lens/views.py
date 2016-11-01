from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. Welcome to WhoGovs.")

def representative(request, rep_id):
    return HttpResponse("You have requested "+rep_id)