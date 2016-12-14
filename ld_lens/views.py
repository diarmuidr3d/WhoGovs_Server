from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from ld_lens.models import Person, RepInConstituency


def index(request):
    return HttpResponse("Hello, world. Welcome to WhoGovs.")


def person(request, person_id):
    template = loader.get_template('ld_lens/person.html')
    person = Person.objects.get(person_id=person_id)
    context = {
        'name': str(person.name),
        'born_on': person.born_on,
        'died_on': person.died_on,
        'repin': RepInConstituency.objects.filter(representative=person)
    }
    return HttpResponse(template.render(context, request))