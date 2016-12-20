from __future__ import unicode_literals

from django.db import models


class Contactable(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    facebook = models.CharField(max_length=50, null=True, blank=True)
    twitter = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)


class Profession(models.Model):
    title = models.CharField(max_length=150)


class Person(Contactable):
    person_id = models.IntegerField(primary_key=True)
    born_on = models.DateField(verbose_name='Date of Birth', null=True, blank=True)
    died_on = models.DateField(verbose_name='Date of Death', null=True, blank=True)
    has_profession = models.ManyToManyField(Profession, blank=True)


class Constituency(models.Model):
    name = models.CharField(max_length=100)


class TemporalRecord(models.Model):
    temp_record_id = models.AutoField(primary_key=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class Party(Contactable, TemporalRecord):

    has_preceeding_party = models.ManyToManyField('self')


class House(models.Model):
    house_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)


class HouseSitting(TemporalRecord):
    number = models.IntegerField()
    seats = models.IntegerField()
    belongs_to = models.ForeignKey(House, null=True, blank=True)

    class Meta:
        unique_together = ('belongs_to', 'number')

class Election(models.Model):
    date = models.DateField('Date of Election')


class ConstituencyRecord(models.Model):
    constituency_record_id = models.AutoField(primary_key=True)
    for_constituency = models.ForeignKey(Constituency)


class RepresentativeRecord(models.Model):
    rep_record_id = models.AutoField(primary_key=True)
    representative = models.ForeignKey(Person, on_delete=models.CASCADE)


class RepInConstituency(ConstituencyRecord, TemporalRecord, RepresentativeRecord):
    # This start and end date should only be filled if different to the house sitting
    for_party = models.ForeignKey(Party, null=True, blank=True)
    for_house_sitting = models.ForeignKey(HouseSitting)


class ElectionRecord(ConstituencyRecord, models.Model):
    part_of = models.ForeignKey(Election)
    for_candidate = models.ForeignKey(RepInConstituency)


class Proceeding(TemporalRecord):
    title = models.CharField(max_length=100)


class ProceedingRecord(models.Model):
    in_proceeding = models.ForeignKey(Proceeding, on_delete=models.CASCADE)


class RepSpoke(ProceedingRecord, RepresentativeRecord):
    content = models.TextField()
    order = models.IntegerField()


class RepWrote(ProceedingRecord, RepresentativeRecord):
    content = models.TextField()


class VoteOption(models.Model):
    name = models.CharField(max_length=20)


class RepVoted(ProceedingRecord, RepresentativeRecord):
    vote = models.ForeignKey(VoteOption)


class Role(RepresentativeRecord, TemporalRecord):
    title = models.CharField(max_length=100)
