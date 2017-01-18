import requests
import argparse
import json
import random

from openpyxl import Workbook
from bs4 import BeautifulSoup


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def get_random_courses_list(quantity):
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
        skip_letters_in_launch_date = 20
        index_start_launch_date = course_page_html.find("plannedLaunchDate") + skip_letters_in_launch_date
        index_end_launch_date = index_start_launch_date + course_page_html[index_start_launch_date:].find('"')
        course_info['start_date'] = course_page_html[index_start_launch_date: index_end_launch_date]

    skip_letters_in_workload = 11
    index_start_workload = course_page_html.find("workload") + skip_letters_in_workload
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Courses quantity')
    parser.add_argument('courses_quantity', type=check_positive, help='How many courses to show')
    parser.add_argument("path_to_save", type=str, help="The path where you want to save xlsx.")
    args = parser.parse_args()

    filepath = args.path_to_save
    urls = get_random_courses_list(args.courses_quantity)
    courses_info = []
    for course_number, url in enumerate(urls, start=1):
        courses_info.append(get_course_info(url))
        print("%s course added to general list" % course_number)
    print("%s.xlsx saved" % filepath)
    output_courses_info_to_xlsx(filepath, courses_info)
