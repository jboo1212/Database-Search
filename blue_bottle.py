"""
DISCLAIMER: Please note that I have not included functionality for Refined Search to sites like beyond.com,
glassdoor.com because I find too many sites to be redundant.  That being said, if you would like me to add some more
sites (that I can try and not to hard code), I definitely will.
Some other things I left out: radius, salary expectations, etc, program 'sleeping'
"""

from bs4 import BeautifulSoup
import string
import requests
import time


class RefinedSearchError(Exception):
    def _init_(self, has_failed):
        self.has_failed = has_failed
        return self.has_failed


class RefinedSearch:

    def __init__(self):
        self.default_url = raw_input("Enter the website you want to search but please note, type in the whole url, e.g."
                                     "'http://www.dice.com': ")

        self.user_job = None
        self.user_city = None
        self.user_state = None

    # Renders the url content using the requests module and an html parser/scraper, Beautiful Soup.
    def get_html_content(self, url):

        request = requests.get(url)

        page_content = BeautifulSoup(request.content, 'html.parser')
        return page_content

    """
    Adds robots.txt to the end of the job database website to see if the website will let us scrape.
    A website like linkedin won't let you scrape, for example.
    Websites that will: dice, indeed.
    """
    def get_a_website_we_can_scrape(self):

        self.default_url += '/robots.txt'
        page_data = requests.get(self.default_url).text

        if 'User-agent: *' in page_data and not 'Notice' in page_data :
            self.default_url = self.default_url.strip('/robots.txt')
            return self.default_url

        else:
            raise RefinedSearchError("Website is not scrapable!")

    def search_the_data_inside_the_links_to_get_the_links_we_want(self):

        """
        Gives us a unique list of the links since some of the links we generate could be duplicates (i.e. set).
        We then load the html content from that page, get rid of trash links inside the page and search for the criteria.
        """

        # list of all the links
        refined_job_links_set = set(self.get_all_the_links())
        refined_job_links = []
        for link in refined_job_links_set:
            refined_job_links.append(link)

        extra_refined_job_links = []
        user_job_criteria = string.lower(raw_input("Please enter a list of criteria you would like to search "
                                  "for other than the job title -- e.g. 'intern', 'python', 'associate': "))
        user_job_criteria = user_job_criteria.split()

        for i in range(len(refined_job_links)):

            current_refined_job_page = self.get_html_content(refined_job_links[i])
            if 'dice.com' in self.default_url and not (current_refined_job_page.find(name="div",
                                                                                     attrs={'class': 'mTB10'})) is None:
                current_destroyable_content = current_refined_job_page.find(name="div", attrs={'class': 'mTB10'})
                current_destroyable_content.decompose()
            else:
                pass

            """
            We now get all of the stripped whitespace text, looking for matches and then adding a full match
            to a list where we add the links so the user has a reference for that link.
            """
            current_refined_job_children = string.lower(current_refined_job_page.getText(strip=True))

            input_tracker = 0

            for k in range(len(user_job_criteria)):

                if user_job_criteria[k] in current_refined_job_children:
                    input_tracker += 1
                else:
                    pass

            if input_tracker != len(user_job_criteria):
                pass
            else:
                extra_refined_job_links.append(refined_job_links[i])

        return extra_refined_job_links

    # Some semi-hard-coded string formatting.
    def get_page_with_links_on_it(self):

        self.default_url += "/jobs?q=%s+&l=%s%s2C+%s" % (self.get_job_title(), self.get_city(), '%', self.get_state())
        new_page_content = self.get_html_content(self.default_url)

        return new_page_content

    def get_all_the_links(self):
        """
        Finds all the link references ("a") in the html document that we loaded -- then,
        we take a more stringent approach on the criteria by only looking at text (Dice.com) or
        certain class attributes (Indeed.com).
        For some reason, the href elements scraped from indeed cut off 'indeed.com' so we add it back in.
        """
        current_page = self.get_page_with_links_on_it()
        current_page_link_elements = current_page.find_all(name="a")

        http_indeed = "http://www.indeed.com"

        most_current_page_link_elements = []

        len_elements = len(current_page_link_elements)

        for j in range(len_elements):

            if self.user_job in current_page_link_elements[j].getText(strip=True) and 'radius' \
                    not in current_page_link_elements[j]['href']:

                most_current_page_link_elements.append(current_page_link_elements[j]['href'])

            try:
                # This is for the case that the job title is inside the class 'title'
                # because there was no good text element to scrape.
                if self.user_job in current_page_link_elements[j]['title'] and 'radius' \
                        not in current_page_link_elements[j]['href']:

                    most_current_page_link_elements.append(current_page_link_elements[j]['href'])

            except KeyError:
                pass

        if 'http://www.indeed.com' in self.default_url:

            for k in range(len(most_current_page_link_elements)):
                temp_current_links = most_current_page_link_elements[k]
                most_current_page_link_elements[k] = '%s%s' % (http_indeed, temp_current_links)

        else:
            pass

        return most_current_page_link_elements

    # Returns the job title with the concatenation formatting
    def get_job_title(self):

        self.user_job = string.capwords(raw_input("Please enter the job you would like to search for such as "
                                                  "'software engineer' or \n'business analyst' but "
                                                  "please note, use only one or two words: "))

        concatenated_user_job = self.concat_words(self.user_job)
        return concatenated_user_job

    # Returns the city name with the concatenation formatting
    def get_city(self):

        self.user_city = string.capwords(raw_input("Please enter the city you would like to search your "
                                                   "job in like 'Irvine' or 'Santa Monica': "))

        concatenated_user_city = self.concat_words(self.user_city)
        return concatenated_user_city

    # Returns the state name
    def get_state(self):

        self.user_state = string.capitalize(raw_input("Please enter the state you would like to search for using "
                                                      "only the abbreviations like 'CA' or 'NY': "))
        return self.user_state

    """
    Whitespaces can be found at the end of the raw_input string so
    we account for none or -1.  Also, if we find a whitespace we locate the position
    and then format the whitespace with a '+' sign in the url.
    """
    def concat_words(self, user_input):

        if user_input.find(" ") is None or user_input.find(" ") == -1:
            pass
        else:
            whitespace_position_job = user_input.find(" ")
            user_input= user_input[:whitespace_position_job] + '+' + user_input[whitespace_position_job:]
            user_input = user_input.replace(" ", "")

        return user_input

    # Adds some numbers/readability to the potential big wall of text in your editor/sys.out page
    def number_the_links(self):
        links = self.search_the_data_inside_the_links_to_get_the_links_we_want()

        for i in range(len(links)):
            temp_links = links[i]
            links[i] = '%d) %s' % (i+1, temp_links)
            print links[i], '\n'


def main():

    start_time = time.time()
    refined_search = RefinedSearch()
    refined_search.get_a_website_we_can_scrape()
    refined_search.number_the_links()
    print "Your search was completed in: ", (time.time() - start_time) / 60, "minutes"

if __name__ == "__main__":
    main()
