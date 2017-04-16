from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from ld_lens.models import Person, RepInConstituency, Constituency, Party


def index(request):
    return HttpResponse("Hello, world. Welcome to WhoGovs.")


def person(request, person_id):
    template = loader.get_template('ld_lens/person.html')
    person = Person.objects.get(person_id=person_id)
    context = {
        'name': str(person.name),
        'born_on': person.born_on,
        'died_on': person.died_on,
        'person': person,
        'repin': RepInConstituency.objects.filter(representative=person),
        'jobs': person.jobs.all()
    }
    return HttpResponse(template.render(context, request))


def constituency(request, name):
    template = loader.get_template('ld_lens/constituency.html')
    this_constituency = Constituency.objects.get(name=name)
    reps_in = this_constituency.repinconstituency_set.all()
    context = {
        'name': name,
        'reps_in': reps_in
    }
    return HttpResponse(template.render(context, request))


def party(request, name):
    template = loader.get_template('ld_lens/party.html')
    this_party = Party.objects.get(name=name)
    print(this_party.repinconstituency_set.all())
    context = {
        'name': this_party.name,
        'preceeding_party': this_party.has_preceeding_party.name,
        'representatives':  Person.objects.filter(repinconstituency__for_party=this_party).distinct()
    }
    return HttpResponse(template.render(context, request))