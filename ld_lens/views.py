from django.shortcuts import render
from django.http import HttpResponse
from ld_lens.models import Person


def index(request):
    return HttpResponse("Hello, world. Welcome to WhoGovs.")


def person(request, person_id):
    return HttpResponse("You have requested "+str(Person.objects.get(person_id=person_id).name))