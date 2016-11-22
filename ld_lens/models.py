from __future__ import unicode_literals

from django.db import models


class Contactable(models.Model):
    name = models.CharField(verbose_name='Full Name', max_length=50)
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
    has_profession = models.ManyToManyField(Profession, null=True, blank=True)


class Constituency(models.Model):
    name = models.CharField(max_length=100)


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    belongs_to = models.ForeignKey('self', null=True, blank=True)


class Election(models.Model):
    date = models.DateField('Date of Election')


class ConstituencyRecord(models.Model):
    constituency_record_id = models.AutoField(primary_key=True)
    for_constituency = models.ForeignKey(Constituency)


class TemporalRecord(models.Model):
    temp_record_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class RepresentativeRecord(models.Model):
    rep_record_id = models.AutoField(primary_key=True)
    representative = models.ForeignKey(Person, on_delete=models.CASCADE)


class RepInConstituency(ConstituencyRecord, TemporalRecord, RepresentativeRecord):
    for_organisation = models.ManyToManyField(Organisation, null=True, blank=True)


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


class Membership(RepresentativeRecord, TemporalRecord):
    membership_id = models.AutoField(primary_key=True)
    member_of = models.ForeignKey(Organisation, on_delete=models.CASCADE)


class Role(RepresentativeRecord, TemporalRecord):
    title = models.CharField(max_length=100)
