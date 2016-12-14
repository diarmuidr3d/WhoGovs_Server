import re
import requests
from lxml import html
from datetime import datetime
from Scraper import to_str_new, encode

# from ld_lens.models import Organisation as House

class HouseScraper:
    house_0 = "Dail"
    house_1 = "Seanad"
    xpath_details = "id('tabs-1')/text()"

    def scrape_details(self, house_type, house_number):
        url = "http://www.oireachtas.ie/members-hist/default.asp?housetype=" + str(house_type) + "&HouseNum=" + str(house_number)
        content = requests.get(url).content
        page = html.fromstring(content)
        house_details = page.xpath(self.xpath_details)
        self.parse_house_details(house_details)

    def parse_house_details(self, house_details):
        """
        Splits the list of xpath results returned from the oireactas website into meaningful data
        :type house_details: list
        """
        print(house_details)
        for each in house_details:
            normalised_string = to_str_new(each).strip()
            print (normalised_string)
            if "Period:" in normalised_string:
                self.parse_period(normalised_string)

    def parse_period(self, period_string):
        """
        Splits a string passed in in the form: 'Period: DD Month YYYY - DD Month YYYY' into tow dates
        :type period_string: str
        """
        index_of_dash = period_string.find('-')
        start_date = period_string[period_string.find(':')+1:index_of_dash].strip()
        end_date = period_string[index_of_dash+1:].strip()
        print(self.parse_date(start_date), self.parse_date(end_date))

    def parse_date(self, date_string):
        return datetime.strptime(date_string, '%d %B %Y')


hs = HouseScraper()
hs.scrape_details(0, 25)