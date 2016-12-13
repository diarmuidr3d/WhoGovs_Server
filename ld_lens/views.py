from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from ld_lens.models import Person


def index(request):
    return HttpResponse("Hello, world. Welcome to WhoGovs.")


def person(request, person_id):
    template = loader.get_template('ld_lens/person.html')
    context = {
        'name': str(Person.objects.get(person_id=person_id).name),
    }
    return HttpResponse(template.render(context, request))