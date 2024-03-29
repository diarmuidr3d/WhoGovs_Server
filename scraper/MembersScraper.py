import re
import requests
from lxml import html
from datetime import date, datetime
from scraper.Scraper import to_str

from ld_lens.models import Person as Representative, RepInConstituency, Constituency, Party, House, Role,\
    HouseSitting, Profession, JobForPerson, RepRole, HouseSittingRole

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
    xpath_roles = '//h5[text()="Details"]/following-sibling::*[1]/text()'
    xpath_sitting_url = "//li/b[text() = 'House: ']/a/@href"
    xpath_email = "//a[contains(@href, 'mailto:')]/text()"
    xpath_contact = "//h5[text()='Address']/following-sibling::*[1]"

    def scrape_details(self, member_id):
        content = requests.get(self.members_url + to_str(member_id)).content
        page = html.fromstring(content)
        member_name = page.xpath(self.xpath_name)
        print(member_name)
        if len(member_name) == 1:
            member_name = member_name[0]
            lifetime = page.xpath(self.xpath_life)
            if len(lifetime) == 1:
                lifetime = self.parse_lifetime(lifetime[0])
            else:
                lifetime = (None, None)
            all_constituencies = page.xpath(self.xpath_all_constituency)
            all_parties = page.xpath(self.xpath_all_parties)
            all_appointments = page.xpath(self.xpath_roles)
            all_sitting_urls = page.xpath(self.xpath_sitting_url)
            (address, email, phone,  website) = self.__parse_contact_details(page)
            representative = Representative(person_id=member_id, name=member_name, born_on=lifetime[0],
                                            died_on=lifetime[1], email=email, website=website, postal_address=address)
            representative.save()
            self.__add_professions_from_page(representative, page)
            if len(all_appointments) > 0:
                self.__parse_roles(all_appointments, representative)
            for each in range(0, len(all_constituencies)):
                constituency = Constituency.objects.get_or_create(name=all_constituencies[each])[0]
                # TODO: Add start / end dates for TDs who were elected / removed mid-term
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

    def __parse_contact_details(self, page):
        contact_details = page.xpath(self.xpath_contact)
        address = ""
        website = None
        email = None
        phone = None
        if contact_details:
            text = contact_details[0].text_content().split("\r\n")
            if len(text) is not 0:
                for each in text:
                    line = each.strip()
                    print(line)
                    search = re.search("^([WTE]:)(.*)$", line)
                    if search is not None:
                        print(search.group(0), search.group(1), search.group(2))
                    if search is None:
                        address += ", " + line
                    elif search.group(1) == "W:":  # Website
                        website = search.group(2).strip()
                    elif search.group(1) == "T:":  # Phone
                        phone = search.group(2).strip()
                    elif search.group(1) == "E:":  # email
                        email = search.group(2).strip()
        if address == "":
            address = None
        return address, email, phone, website

    def __add_professions_from_page(self, representative, page):
        """
        Extracts the professions for a Person from their page and adds the relationships / objects as needed
        :type representative: Person
        """
        professions = page.xpath(self.xpath_profession)
        if len(professions) == 1:
            professions = self.parse_professions(professions[0])
            for each in professions:
                JobForPerson.objects.get_or_create(person=representative, profession=each)
        representative.save()

    @staticmethod
    def __parse_party_name(party_name):
        """
        :type party_name: str
        """
        party_name = to_str(party_name)
        # source_chars = "_"
        # destin_chars = " "
        # table = maketrans(source_chars, destin_chars)
        # party_name = party_name.translate(table, ":")
        party_name = party_name.replace("_", " ")
        party_name = party_name.strip()
        return party_name

    @staticmethod
    def __parse_sitting_urls(sitting_url):
        regex = r'(?:housetype=)(\d*)(?:&HouseNum=)(\d*)'
        split = re.search(regex, sitting_url)
        return split.group(1), split.group(2)

    @staticmethod
    def __parse_roles(details, representative):
        """
        Parses the roles listed in the "Details" section of the Representative page
        :param details: The list of text from the Details Section eg: ['1st Dail - Title 1', '2nd Dail - Title 2']
        :param representative: The Representative who held these Roles
        :return: None
        """

        def create_rep_role(role_title, role_start_date, role_end_date, role_representative, role_sitting):
            """
            Creates (or gets if already existing) the Role, HouseSittingRole and RepRole for the inputs
            This method was created to avoid duplication of code
            :param role_title: String containing the title of the Role
            :param role_start_date: The start date for which the Representative held the role
            :param role_end_date: The end date for which the Representative held the role
            :param role_representative: The Representative who held the Role
            :param role_sitting: The HouseSitting for which the Representative held this role
            :return: None
            """
            role = Role.objects.get_or_create(title=role_title)[0]
            hsr = HouseSittingRole.objects.get_or_create(role=role, house_sitting=role_sitting)[0]
            rep_role = RepRole.objects.get_or_create(representative=role_representative, start_date=role_start_date,
                                                     end_date=role_end_date, house_sitting_role=hsr)[0]
            rep_role.save()

        current_sitting = None
        for each in details:  # for each line in the details list
            text = to_str(each).strip()
            title_search = re.search(r"^(\d{1,2})\w{2}\s(\w{4,6})\s*-\s*([^\[]*)", text)  # Grab the sitting and title
            if title_search:
                house_number = title_search.group(1)
                house_name = title_search.group(2)
                title = title_search.group(3).strip()
                house = House.objects.get(name=house_name)
                current_sitting = HouseSitting.objects.get(number=house_number, belongs_to=house)
                bracket_index = text.find('[')
                if bracket_index != -1:
                    date_text = text[bracket_index + 1:text.find(']')]  # Extract the date of the roles from the title
                    dates_found = re.findall(r"\d{1,2}\s\w{3,9}\s\d{4}", date_text)  # Find dates within the date text
                    if len(dates_found) is not 0:
                        if len(dates_found) % 2 is 1:
                            print("**FLAG 1.1: Uneven number of dates returned")
                        else:
                            for each_index in range(0, len(dates_found), 2):
                                # Step in twos as dates alternate between start and end eg: Start, End, Start 2, End 2
                                start_date = datetime.strptime(dates_found[each_index], "%d %B %Y")
                                end_date = datetime.strptime(dates_found[each_index + 1], "%d %B %Y")
                                create_rep_role(title, start_date, end_date, representative, current_sitting)
                    else:
                        print("**FLAG 1.2: No dates found in " + date_text)
            elif current_sitting is None:
                print("** FLAG 1.3: The following details could not be parsed: '" + text + "'")

    @staticmethod
    def parse_professions(professions):
        index = professions.find(',')
        if index == -1:
            return [Profession.objects.get_or_create(title=professions.strip())[0]]
        else:
            profession_name = professions[:index]
            profession = Profession.objects.get_or_create(title=profession_name.strip())[0]
            professions = professions[index + 1:]
            return_value = MembersScraper.parse_professions(professions)
            return_value.append(profession)
            return return_value

    @staticmethod
    def parse_lifetime(lifetime):
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
