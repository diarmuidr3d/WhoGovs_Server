import re
import requests
from lxml import html
from datetime import date
from string import maketrans
from Scraper import to_str

from ld_lens.models import Person as Representative, RepInConstituency, Constituency, Party, House, Role, HouseSitting, \
    Profession, JobForPerson, RepRole

dail_members_url = 'http://www.oireachtas.ie/members-hist/default.asp?housetype=0'
seanad_members_url = 'http://www.oireachtas.ie/members-hist/default.asp?housetype=1'


class MembersScraper:
    members_url = "http://www.oireachtas.ie/members-hist/default.asp?MemberID="
    xpath_name = "//div[@class='memberdetails']/h3/text()"
    xpath_life = "//div[@class='memberdetails']/p[1]/text()"
    xpath_profession = "//h5[text() = 'Profession: ']/span/text()"
    xpath_party = "//li[span/text() = 'Party']/text()"
    xpath_all_house = "//b[text() = 'House: ']/a/text()"
    xpath_all_constituency = "//li[span/text() = 'Constituency']/a/text()"
    xpath_all_parties = "//li[span/text() = 'Party']/text()"
    xpath_appointments = '//h5[text()="Details"]/following-sibling::*[1]/text()'
    xpath_sitting_url = "//li/b[text() = 'House: ']/a/@href"

    def scrape_details(self, member_id):
        content = requests.get(self.members_url + to_str(member_id)).content
        page = html.fromstring(content)
        member_name = page.xpath(self.xpath_name)
        print(member_name)
        if len(member_name) == 1:
            member_name = member_name[0]
            lifetime = page.xpath(self.xpath_life)
            if len(lifetime) == 1:
                lifetime = self.__parse_lifetime(lifetime[0])
            else:
                lifetime = (None, None)
            all_constituencies = page.xpath(self.xpath_all_constituency)
            all_parties = page.xpath(self.xpath_all_parties)
            all_appointments = page.xpath(self.xpath_appointments)
            all_sitting_urls = page.xpath(self.xpath_sitting_url)
            print(lifetime[0])
            representative = Representative(person_id=member_id, name=member_name, born_on=lifetime[0],
                                            died_on=lifetime[1])
            representative.save()
            self.__add_professions_from_page(representative, page)
            if len(all_appointments) > 0:
                # TODO: Assign these
                print all_appointments
                appointments = self.__parse_appointments(all_appointments, representative)
                print appointments
            for each in range(0, len(all_constituencies)):
                constituency = Constituency.objects.get_or_create(name=all_constituencies[each])[0]
                # TODO: Add start / end dates
                (house_type, house_number) = self.__parse_sitting_urls(all_sitting_urls[each])
                house = House.objects.get(house_id=house_type)
                sitting = HouseSitting.objects.get(number=house_number, belongs_to=house)
                rep_record = RepInConstituency.objects.get_or_create(for_constituency=constituency,
                                                                     representative=representative,
                                                                     for_house_sitting=sitting)[0]
                rep_record.save()
                if len(all_parties) > each:
                    party_name = self.__parse_party_name(all_parties[each])
                    if Party.objects.filter(name=party_name):
                        party = Party.objects.get(name=party_name)
                    else:
                        party = Party(name=party_name)
                        party.save()
                    rep_record.for_party = party
                    rep_record.save()
            return True
        else:
            print("no data found for id: ", member_id)
            return False

    def __add_professions_from_page(self, representative, page):
        """
        Extracts the professions for a Person from their page and adds the relationships / objects as needed
        :type representative: Person
        """
        professions = page.xpath(self.xpath_profession)
        if len(professions) == 1:
            professions = self.__parse_professions(professions[0])
            for each in professions:
                JobForPerson.objects.get_or_create(person=representative, profession=each)
        representative.save()

    @staticmethod
    def __parse_party_name(party_name):
        """
        :type party_name: str
        """
        party_name = to_str(party_name)
        source_chars = "_"
        destin_chars = " "
        table = maketrans(source_chars, destin_chars)
        party_name = party_name.translate(table, ":")
        party_name = party_name.strip()
        return party_name

    @staticmethod
    def __parse_sitting_urls(sitting_url):
        regex = r'(?:housetype=)(\d*)(?:&HouseNum=)(\d*)'
        split = re.search(regex, sitting_url)
        return split.group(1), split.group(2)

    @staticmethod
    def __parse_appointments(details, representative):
        # TODO: Finish this method, grab the correct house sitting and then create the roles, etc
        current_sitting = None
        return_values = {}
        for each in details:
            text = to_str(each).strip()
            if '-' in text:
                index = text.find('-')
                sitting_text = text[:index].strip()
                print sitting_text
                house_number = re.search(r'[0-9]+', sitting_text).group(0)
                # house_number = int(sitting_text[:sitting_text.find(' ')].strip())
                house_name = sitting_text[sitting_text.find(' '):].strip()
                house = House.objects.get(name=house_name)
                print sitting_text, " = ", house_number, " - ", house_name
                current_sitting = HouseSitting.objects.get(number=house_number, belongs_to=house)
                text = text[index + 1:].strip()
            elif current_sitting is None:
                print "** FLAG: The following details could not be parsed: '" + text + "'"
            if current_sitting not in return_values:
                return_values[current_sitting] = []
            print text
            # rep_role = RepRole(representative=representative, start_date=date(1916, 1, 1), title=text, house_sitting=current_sitting)
            # rep_role.save()
            # return_values[current_sitting].append(rep_role)
        # return return_values

    def __parse_professions(self, professions):
        index = professions.find(',')
        if index == -1:
            return [Profession.objects.get_or_create(title=professions.strip())[0]]
        else:
            profession_name = professions[:index]
            profession = Profession.objects.get_or_create(title=profession_name.strip())[0]
            professions = professions[index + 1:]
            return_value = self.__parse_professions(professions)
            return_value.append(profession)
            return return_value

    @staticmethod
    def __parse_lifetime(lifetime):
        """
        Assuming it's in the form (DD/MM/YYYY - DD/MM/YYYY)
        :type lifetime: str
        """

        def parse_date(date_to_parse):
            slash = date_to_parse.find('/')
            dayval = date_to_parse[:slash]
            day = int(dayval)
            my = date_to_parse[slash + 1:]
            secondslash = my.find('/')
            month = int(my[:secondslash])
            year = int(my[secondslash + 1:])
            return date(year, month, day)

        open_bracket = lifetime.find('(')
        close_bracket = lifetime.find(')')
        separator = lifetime.find('-')
        born = lifetime[open_bracket + 1:separator]
        died = lifetime[separator + 1:close_bracket]
        born = born.strip()
        died = died.strip()
        if born == '':
            born = None
        else:
            born = parse_date(born)
        if died == '':
            died = None
        else:
            died = parse_date(died)
        return born, died
