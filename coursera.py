import sys
from bs4 import BeautifulSoup
import requests
import json
import random
import re
from pprint import pprint


def get_courses_list(quantity):
    response = requests.get('https://www.coursera.org/sitemap~www~courses.xml')
    courses_soup = BeautifulSoup(response.text, 'xml')
    course_url_list = courses_soup.urlset.find_all('loc')
    return [x.string for x in random.sample(course_url_list, quantity)]


def get_course_info(course_slug):
    pass


def output_courses_info_to_xlsx(filepath):
    pass


if __name__ == '__main__':
    pass

urls = get_courses_list(quantity=20)

url = urls[0]

response = requests.get(url)
response.encoding = 'utf-8'
course_page_html = response.text
course_page_soup = BeautifulSoup(course_page_html, 'lxml')

with open('file.txt', 'w', encoding='utf-8') as f:
    f.write(course_page_html)

print(url)
try:
    course_info_str = course_page_soup.find("script", {"type": "application/ld+json"}).text
    course_info = json.loads(course_info_str)
    course_start_date = course_info['hasCourseInstance'][0]['startDate']
    print('Start date:', course_start_date)
    print('Title:', course_info['name'].encode('utf-8').decode('cp1251'))
except:
    index_start_launch_date = course_page_html.find("plannedLaunchDate") + 20
    index_end_launch_date = index_start_launch_date + course_page_html[index_start_launch_date:].find('"')
    course_launch_date = course_page_html[index_start_launch_date: index_end_launch_date]
    print('Launch date:', course_launch_date)

index_start_workload = course_page_html.find("workload") + 11
index_end_workload = index_start_workload + course_page_html[index_start_workload:].find('"')
course_workload = course_page_html[index_start_workload: index_end_workload]
if not course_workload:
    course_workload = '-'
print('Workload:', course_workload)


course_language = course_page_soup.find("div", {"class": "language-info"}).text
print('Language:', course_language)
try:
    course_rating = course_page_soup.find("div", {"class": "ratings-text bt3-visible-xs"}).text
except:
    course_rating = '-'
print('Rating:', course_rating)