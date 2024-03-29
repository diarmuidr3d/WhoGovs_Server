import os
import sys

import datetime

from django.core.management import BaseCommand

from scraper.MembersScraper import MembersScraper
from scraper.HouseScraper import HouseScraper
# from scraper.DebatesScraper import DebatesScraper
# from Objects import MyGraph
import traceback


class Command(BaseCommand):
    help = 'Runs the Scraper'

    # def add_arguments(self, parser):
        # parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        scrape_all_houses()
        scrape_all_members()

def scrape_all_houses():
    dail_num = 1
    house_scraper = HouseScraper()
    #TODO: Autodetect the last sitting, don't rely on these numbers
    while dail_num < 33:  # Gets the Dail
        house_scraper.scrape_details(0, dail_num)
        dail_num += 1
    seanad_num_first = 1
    while seanad_num_first < 26: # Next two get the Seanad
        house_scraper.scrape_details(1, seanad_num_first)
        seanad_num_first += 1
    other_seanad_numbers = (1922, 1925, 1928, 1931, 1934)
    for each in other_seanad_numbers:
        house_scraper.scrape_details(1, each)

def scrape_all_members():
    # MembersScraper().scrape_details(6)
    rep_id = 1
    scraper = MembersScraper()
    false_count = 0
    while false_count < 5:
        print(rep_id)
        return_value = scraper.scrape_details(rep_id)
        if return_value:
            false_count = 0
        else:
            false_count += 1
        rep_id += 1


def scrape_all_debates():
    dail = "dail"
    seanad = "seanad"
    earliest_year = 1919
    current_year = datetime.datetime.now().year
    debates_scraper = DebatesScraper(graph)
    debates_scraper.get_debate_urls_for_year(dail, current_year)
    # debates_scraper.get_debate_urls_for_year(seanad, current_year)
    # while current_year >= earliest_year:
    #     DebatesScraper.get_debate_urls_for_year(dail, current_year)
    #     DebatesScraper.get_debate_urls_for_year(seanad, current_year)
    #     current_year -= 1


if __name__ == "__main__":
    # graph = MyGraph()
    try:
        scrape_all_members()
        # scrape_all_debates()
    except (KeyboardInterrupt, SystemExit, Exception) as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print exception: ***")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        print("*** Exception over ***")
    #     graph.export("whogovs.n3")
    # graph.export("whogovs.n3")