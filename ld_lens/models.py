from __future__ import unicode_literals

from django.db import models


class Contactable(models.Model):
    name = models.CharField(verbose_name='Full Name', max_length=50)
    email = models.EmailField()
    facebook = models.CharField(max_length=50)
    twitter = models.CharField(max_length=50)
    website = models.CharField(max_length=100)


class Person(Contactable):
    id = models.IntegerField(primary_key=True)
    born_on = models.DateField(verbose_name='Date of Birth')
    died_on = models.CharField(verbose_name='Date of Death')
    has_profession = models.ManyToManyField(Profession)


class Representative(Person):
    record = models.ForeignKey(RepresentativeRecord, on_delete=models.CASCADE)


class Profession(models.Model):
    title = models.CharField(max_length=150)


class Constituency(models.Model):
    name = models.CharField(max_length=100)


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    belongs_to = models.ForeignKey('self')
    has_belonging = models.ForeignKey('self')

# TODO: uncomment these if needed
# class Party(Contactable, Organisation):
#
#
#
# class Legislature(Organisation):
#
#
#
# class Committee(Legislature):
#
#
#
# class House(Legislature):


class Election(models.Model):
    date = models.DateField('Date of Election')


class ConstituencyRecord(models.Model):
    for_constituency = models.ForeignKey(Constituency)


class ElectionRecord(ConstituencyRecord, models.Model):
    part_of = models.ForeignKey(Election)
    for_candidate = models.ForeignKey(RepInConstituency)


class TemporalRecord(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()


class RepresentativeRecord(models.Model):
    representative = models.ForeignKey(Representative)


# class OrganisationRecord(models.Model):
#     for_organisation = models.ManyToManyField(Organisation)


class RepInConstituency(ConstituencyRecord, TemporalRecord, RepresentativeRecord):
    for_organisation = models.ForeignKey(Organisation)


class Proceeding(TemporalRecord):
    title = models.CharField(max_length=100)


# class Debate(Proceeding):


# class Vote(Proceeding):


class ProceedingRecord(models.Model):
    in_proceeding = models.ForeignKey(Proceeding, on_delete=models.CASCADE)


class RepSpoke(ProceedingRecord, RepresentativeRecord):
    representative = models.ForeignKey(Representative, on_delete=models.CASCADE)
    content = models.CharField()
    order = models.IntegerField()


class RepWrote(ProceedingRecord, RepresentativeRecord):
    content = models.CharField()


class RepVoted(ProceedingRecord, RepresentativeRecord):
    vote = models.ForeignKey(VoteOption)


class Membership(RepresentativeRecord, TemporalRecord):
    member_of = models.ForeignKey(Organisation, on_delete=models.CASCADE)


class Role(RepresentativeRecord, TemporalRecord):
    title = models.CharField(max_length=100)


class VoteOption(models.Model):
    name = models.CharField(max_length=20)
