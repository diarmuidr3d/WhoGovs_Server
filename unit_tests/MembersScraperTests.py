# import unittest
from django.test import TestCase
from datetime import date

from scraper.MembersScraper import MembersScraper


class MembersScraperTests(TestCase):

    def test_parse_lifetime(self):
        lifetime = "(15/06/1997 - 12/08/2012)"
        born_should = date(year=1997, month=6, day=15)
        died_should = date(year=2012, month=8, day=12)
        born, died = MembersScraper.parse_lifetime(lifetime)
        self.assertTrue(born == born_should, msg='Date of birth is not equal to what it should')
        self.assertTrue(died == died_should, msg='Date of death is not equal to what is should')