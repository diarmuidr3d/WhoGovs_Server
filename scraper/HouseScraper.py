import re
import requests
from lxml import html
from datetime import datetime
from Scraper import to_str_new, encode

from ld_lens.models import House, HouseSitting


class HouseScraper:
    xpath_details = "id('tabs-1')/text()"

    def get_house_from_type(self, house_type):
        if House.objects.filter(house_id=house_type).exists():
            return House.objects.get(house_id=house_type)
        else:
            name = "Unknown"
            if house_type is 0:
                name = "Dail"
            elif house_type is 1:
                name = "Seanad"
            house = House(house_id=house_type, name=name)
            house.save()
            return house

    def scrape_details(self, house_type, house_number):
        house = self.get_house_from_type(house_type)
        if not HouseSitting.objects.filter(belongs_to=house, number=house_number).exists():
            url = "http://www.oireachtas.ie/members-hist/default.asp?housetype=" + str(house_type) + "&HouseNum=" + str(house_number)
            content = requests.get(url).content
            page = html.fromstring(content)
            house_details = page.xpath(self.xpath_details)
            if house_details:
                sitting = HouseSitting(belongs_to=house, number=house_number)
                print("Got " + house.name + " " + str(house_number))
                self.parse_house_details(house_details, sitting)
            else:
                return False
        else:
            print("Already exists for house " + str(house_type) + ", sitting " + str(house_number))
        return True

    def parse_house_details(self, house_details, sitting):
        """
        Splits the list of xpath results returned from the oireactas website into meaningful data
        :type house_details: list
        """
        for each in house_details:
            normalised_string = to_str_new(each).strip()
            if "Period:" in normalised_string:
                period = self.parse_period(normalised_string)
                print("Period: " + str(period))
                sitting.start_date = period[0]
                sitting.end_date = period[1]
            if "Seats:" in normalised_string:
                seats = self.parse_seats(normalised_string)
                print("Seats: " + str(seats))
                sitting.seats = seats
        sitting.save()

    def parse_seats(self, seats_string):
        return int(seats_string[seats_string.find(':')+1:].strip())

    def parse_period(self, period_string):
        """
        Splits a string passed in in the form: 'Period: DD Month YYYY - DD Month YYYY' into tow dates
        :type period_string: str
        """
        index_of_dash = period_string.find('-')
        start_date = period_string[period_string.find(':')+1:index_of_dash].strip()
        end_date = period_string[index_of_dash+1:].strip()
        return self.parse_date(start_date), self.parse_date(end_date)

    def parse_date(self, date_string):
        return datetime.strptime(date_string, '%d %B %Y')