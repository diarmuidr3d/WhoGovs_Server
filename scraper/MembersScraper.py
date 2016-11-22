import re
import requests
# from Objects import Representative, RepInConstituency, Constituency, Party, House, Role
from lxml import html
from datetime import date as Date, date
from Scraper import to_str, encode

from ld_lens.models import Person as Representative, RepInConstituency, Constituency, Organisation as Party, Organisation as House, Role

dail_members_url = 'http://www.oireachtas.ie/members-hist/default.asp?housetype=0'
seanad_members_url = 'http://www.oireachtas.ie/members-hist/default.asp?housetype=1'

house_instances_selector = "html body div#limiter div#container.container div.row div.col-xs-12 div.row div.col-md-9.col-xs-12.col-md-push-3.column-center2 div.column-center-inner div table tbody tr"


class MembersScraper:
    members_url = "http://www.oireachtas.ie/members-hist/default.asp?MemberID="
    xpath_name = "//div[@class='memberdetails']/h3/text()"
    xpath_life = "//div[@class='memberdetails']/p[1]/text()"
    xpath_profession = "//h5[text() = 'Profession: ']/span/text()"
    xpath_party = "//h5[text() = 'Party: ']/span/text()"
    xpath_all_house = "//b[text() = 'House: ']/a/text()"
    xpath_all_constituency = "//li[span/text() = 'Constituency']/a/text()"
    xpath_all_parties = "//li[span/text() = 'Party']/text()"
    xpath_appointments = "/html/body/div/div/div/div[1]/div[2]/div[1]/div/div[1]/div[6]/p[3]"

    # def __init__(self, graph):
    #     self.graph = graph

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
            professions = page.xpath(self.xpath_profession)
            if len(professions) == 1:
                professions = self.__parse_professions(professions[0])
            else:
                professions = None
            # party = page.xpath(self.xpath_party)
            # if len(party) == 1:
            #     party = party[0]
            # else:
            #     party = None
            all_houses = page.xpath(self.xpath_all_house)
            all_constituencies = page.xpath(self.xpath_all_constituency)
            all_parties = page.xpath(self.xpath_all_parties)
            all_appointments = page.xpath(self.xpath_appointments)
            # TODO: populate professions into representative
            print(lifetime[0])
            representative = Representative(person_id=member_id, name=member_name, born_on=lifetime[0], died_on=lifetime[1])
            representative.save()
            if len(all_appointments) > 0:
                appointments = self.__parse_appointments(html.tostring(all_appointments[0]), representative)
            for each in range(0, len(all_constituencies)):
                constituency = Constituency(name=all_constituencies[each])
                constituency.save()
                organisations = []
                if len(all_parties) > each:
                    organisations.append(Party(name=all_parties[each]))
                organisations.append(House(name=all_houses[each]))
                # TODO: Add start / end dates
                rep_record = RepInConstituency(for_constituency=constituency, representative=representative)
                rep_record.save()
                rep_record.for_organisation.add(organisations)
                rep_record.save()
            return True
        else:
            print("no data found for id: ", member_id)
            return False

    def __parse_appointments(self, details, representative):
        split_app = re.findall(r">[^<]*<", details)
        current_dail = ""
        return_values = {}
        role_id = 0
        for each in split_app:
            trimmed = each.replace('<', '').replace('>', '').strip()
            if '-' in trimmed:
                index = trimmed.find('-')
                if index != -1:
                    current_dail = trimmed[:index].strip()
                    trimmed = trimmed[index + 1:].strip()
            if current_dail not in return_values:
                return_values[current_dail] = []
            role = Role(representative=representative, start_date=date(1916, 1, 1), title=trimmed)
            role.save()
            return_values[current_dail].append(role)
            role_id += 1
        return return_values

    def __parse_professions(self, professions):
        index = professions.find(',')
        if index == -1:
            return [professions.strip()]
        else:
            profession = professions[:index]
            profession.strip()
            professions = professions[index + 1:]
            retVal = self.__parse_professions(professions)
            retVal.append(profession)
            return retVal

    def __parse_lifetime(self, lifetime):
        """
        Assuming it's in the form (DD/MM/YYYY - DD/MM/YYYY)
        :type lifetime: str
        """

        def parse_date(date):
            slash = date.find('/')
            dayval = date[:slash]
            day = int(dayval)
            my = date[slash + 1:]
            secondslash = my.find('/')
            month = int(my[:secondslash])
            year = int(my[secondslash + 1:])
            return Date(year, month, day)

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
