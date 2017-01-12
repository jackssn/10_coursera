import requests
import json
import random

from openpyxl import Workbook
from bs4 import BeautifulSoup


def get_courses_list(quantity):
    response = requests.get('https://www.coursera.org/sitemap~www~courses.xml')
    courses_soup = BeautifulSoup(response.text, 'html5lib')
    course_url_list = courses_soup.urlset.find_all('loc')
    return [x.string for x in random.sample(course_url_list, quantity)]


def get_course_info(course_slug):
    response = requests.get(course_slug)
    response.encoding = 'utf-8'
    course_page_html = response.text
    course_page_soup = BeautifulSoup(course_page_html, 'html5lib')
    course_info = {'title': '',
                   'language': '',
                   'start_date': '',
                   'workload': '',
                   'rating': '',
                   }
    course_info['title'] = course_page_soup.find("div", {"class": "title display-3-text"}).text
    course_info['language'] = course_page_soup.find("div", {"class": "language-info"}).text

    try:
        course_info_from_script_tag = course_page_soup.find("script", {"type": "application/ld+json"}).text
        course_info_json = json.loads(course_info_from_script_tag)
        course_info['start_date'] = course_info_json['hasCourseInstance'][0]['startDate']
    except AttributeError:
        index_start_launch_date = course_page_html.find("plannedLaunchDate") + 20
        index_end_launch_date = index_start_launch_date + course_page_html[index_start_launch_date:].find('"')
        course_info['start_date'] = course_page_html[index_start_launch_date: index_end_launch_date]

    index_start_workload = course_page_html.find("workload") + 11
    index_end_workload = index_start_workload + course_page_html[index_start_workload:].find('"')
    course_info['workload'] = course_page_html[index_start_workload: index_end_workload]

    try:
        course_info['rating'] = course_page_soup.find("div", {"class": "ratings-text bt3-visible-xs"}).text
    except AttributeError:
        pass

    return course_info


def output_courses_info_to_xlsx(filepath, courses_info):
    wb = Workbook()
    ws = wb.active
    ws.title = "Random courses"
    ws.append(['Title', 'Language', 'Start date', 'Workload', 'Rating'])
    for course_info in courses_info:
        ws.append([course_info['title'],
                   course_info['language'],
                   course_info['start_date'],
                   course_info['workload'],
                   course_info['rating']
                   ])
    wb.save("%s.xlsx" % filepath)
    print("%s saved" % filepath)


if __name__ == '__main__':
    courses_quantity = 10
    filepath = input("Enter filepath (with name xlsx-file without extension) to save your sheet with courses: ")
    urls = get_courses_list(courses_quantity)
    courses_info = []
    for course_number, url in enumerate(urls, start=1):
        courses_info.append(get_course_info(url))
        print("%s course added to general list" % course_number)
    output_courses_info_to_xlsx(filepath, courses_info)
