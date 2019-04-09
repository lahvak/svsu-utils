"""
Module for searching on SVSU Course Schedule website
"""
import bs4
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep


def enter_selection(driver, id, regexp):
    """
    Search drop-down menu options for a regexp and select the first match
    """
    element = driver.find_element_by_id(id)
    choice = next(s for s in element.text.split("\n") if regexp.search(s))
    selector = Select(element)
    selector.select_by_visible_text(choice)
    sleep(1)


def parse_course(course):
    """
    Extract interesting information from a single course listing, and build
    a dictionary from it.
    """
    course_re = r"^([^*]*)\*([^*]*)\*([^(]*)\((\d*)\)\s*(.*)$"
    m = re.match(course_re, course[0])
    return {'dept': m[1],
            'number': m[2],
            'section': m[3],
            'lineno': m[4],
            'name': m[5],
            'instructor': course[2].strip()
            }


def get_course_list(semester_re, dept_re):
    """
    Given a semester regular expression and a department regular expression,
    lists all courses offered by that department in the semester.
    """
    searchurl = "https://webtech.svsu.edu/courses/#!/home#top"

    semester = re.compile(semester_re)
    dept = re.compile(dept_re)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get(searchurl)

    enter_selection(driver, "selectterm", semester)
    enter_selection(driver, "selectdepartment", dept)

    submitbutt = driver.find_element_by_id("courseLookupButton")
    submitbutt.click()

    sleep(1)

    page = bs4.BeautifulSoup(driver.page_source, "lxml")

    driver.quit()

    rowlist = [[cell.getText() for cell in row.find_all("td")]
               for row in page.find_all(id="courseTable")]

    return [parse_course(row) for row in rowlist]
