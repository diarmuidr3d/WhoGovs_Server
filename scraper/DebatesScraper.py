import datetime
from lxml import html
from Objects import Debate, Representative, RepSpoke
from Scraper import to_str, get_page, encode, join_list_unicode_strings

# Committee page by year has significantly different structure to the houses

domain = "http://oireachtasdebates.oireachtas.ie"

xpath_days_for_year = "/html/body/div[1]/div/div/div[3]/div/table/tr/td[2]/a/@href"
xpath_headings_for_debate = "/html/body/div[1]/div/div/div[3]/div/table[2]/tr/td/h3/text()"
xpath_page_content = "/html/body/div[1]/div/div/div[3]/div/table[2]/tr/td"


class DebatesScraper:
    def __init__(self, graph):
        self.graph = graph

    def get_debate_urls_for_year(self, house, year):
        """
        :type year: int
        :type house: str
        """
        url = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=" + \
              house + "&year=" + to_str(year)
        year_page = get_page(url)
        day_urls = year_page.xpath(xpath_days_for_year)
        # for each in day_urls: TODO: uncomment these two lines and remove the line after
        #     get_debate_content(domain + to_str(each), house)
        self.get_debate_content(domain + to_str(day_urls[0]), house)

    def get_debate_content(self, url, house):
        """
        :type url: str
        """
        xpath_heading_text = "text()"
        page_num = 3
        cut_off = url.find(house)+len(house)
        url=url[:cut_off+8]
        datestring = url[cut_off:cut_off+8]
        date = datetime.date(int(datestring[:4]), int(datestring[4:6]), int(datestring[6:]))
        reached_end = False
        current_proceeding = None
        proceeding_content_order = 0
        previous_representative = None
        previous_speech = None
        while not reached_end:
            page = get_page(url + str(page_num).zfill(5))
            print(url + str(page_num).zfill(5))
            page_num += 1
            content = page.xpath(xpath_page_content)
            # reached_end = True # Comment this out to scrape whole day
            if len(content) == 0:
                print("REACHED END")
                reached_end = True
            else:
                content = content[0]
                for child in list(content):
                    if type(child) is html.HtmlElement:
                        tag = child.tag
                        if tag == 'h3':
                            title = to_str(child.xpath(xpath_heading_text)[0])
                            current_proceeding = Debate(self.graph, 1, title, date)
                            proceeding_content_order = 0
                            previous_representative = None
                            previous_speech = None
                        # elif tag == 'h4':
                        #     TODO: Add sub proceedings to the proceeding to allow for individual questions

                        elif tag == 'p':
                            question_number = child.xpath("b[1]/font")
                            if len(question_number) is 0:
                                identifier = "MemberID="
                                rep_url = child.xpath("a[1]/@href")
                                if len(rep_url) is not 0:
                                    rep_url = to_str(rep_url[0])
                                    rep_id = to_str(rep_url[rep_url.find(identifier)+len(identifier):])
                                    representative = Representative(self.graph, rep_id)
                                #     TODO: choose the correct string from the text array
                                text = child.xpath("text()")
                                text = join_list_unicode_strings(text)
                                print text
                                if len(text) > 0:
                                    # text = to_str(text)
                                    text = text.strip()
                                    if text is not "":
                                        if previous_representative is not None and rep_id == previous_representative:
                                            text = previous_speech.content + " " + text
                                            previous_speech.content = text
                                        else:
                                            previous_speech = RepSpoke(self.graph, rep_id + "_" + encode(title) + "_" + to_str(proceeding_content_order), representative, current_proceeding, text, proceeding_content_order,)
                                            current_proceeding.add_proceeding_record(previous_speech)
                                            proceeding_content_order += 1
                            previous_representative = rep_id
