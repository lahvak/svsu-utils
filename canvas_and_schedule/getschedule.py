"""Gets about three semesters of schedules from SVSU registrars website."""
import bs4
from selenium import webdriver

URLBASE = "http://apps.svsu.edu/webapps/courses/#!/professorSearch/{}#top"

def get_classes_schedule(instructor):
    """Scrapes instructor's schedule from SVSU cardinaldirect.  Use the
    intructor's user name here."""
    url = URLBASE.format(instructor)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(chrome_options = options)
    driver.get(url)
    page = bs4.BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    semesters = {}

    headers = page.find_all("h3")
    for h in headers:
        semester = h.getText()
        tab = h.find_next_sibling("table")
        bod = tab.find("tbody")
        courses = [[d.getText() for d in row.find_all("td")] for row in bod.find_all("tr")]

        semesters[semester] = courses

    return semesters
