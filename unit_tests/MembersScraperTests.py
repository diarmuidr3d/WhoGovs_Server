# import unittest
from django.test import TestCase
from datetime import date

from scraper.MembersScraper import MembersScraper
from ld_lens.models import Profession


class MembersScraperTests(TestCase):

    def setUp(self):
        Profession.objects.create(title="Accountant")

    def test_parse_lifetime(self):
        lifetime = "(15/06/1997 - 12/08/2012)"
        born_should = date(year=1997, month=6, day=15)
        died_should = date(year=2012, month=8, day=12)
        born, died = MembersScraper.parse_lifetime(lifetime)
        self.assertTrue(born == born_should, msg='Date of birth is not equal to what it should')
        self.assertTrue(died == died_should, msg='Date of death is not equal to what is should')

    def test_parse_professions(self):
        professions = "Accountant, Public Representative"
        accountant = Profession.objects.get(title="Accountant")
        returned_values = MembersScraper.parse_professions(professions)
        self.assertTrue(len(returned_values) is 2)
        self.assertTrue(accountant in returned_values)
        public_rep = Profession.objects.get(title="Public Representative")
        self.assertTrue(public_rep in returned_values)
