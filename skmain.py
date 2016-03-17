import os
import sys
from bs4 import BeautifulSoup
import requests
from requests.utils import quote
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Style, Font

def parse_foundlocations(locations_html):
    bs_obj = BeautifulSoup(locations_html, "lxml")
    locations_table = bs_obj.find('div', class_ = 'component filter-metro-area search')
    locations = {}
    counter = 1
    for l in locations_table.findAll('li'):
        for link in l.findAll('p'):
            locations.update({counter:[link.a.string, link.a['href']]})
            counter += 1
    return locations

def request_location(location):
    payload = {'utf8':'E29C93', 'query':location}
    result = requests.get('https://www.songkick.com/session/filter_metro_area?', params=payload)
    return result

def choose_locations(locations):
    print "\nLocations found on Songkick"
    print "*****************************"
    for k, v in locations.items():
        print "%s: %s" %(k, v[0])
    print "*****************************"

    while True:
        k = raw_input("Enter the Number of the Location: ")
        if k.isdigit():
            if int(k) in range(1, len(locations)+1):
                return locations[int(k)]
            else:
                continue

def request_events(location, payload=None):
    url = "https://www.songkick.com%s" %location[1]
    if not payload:
        return requests.get(url)
    else:
        return requests.get(url, params=payload)

def parse_events(event_page):
    bs_obj = BeautifulSoup(event_page, "lxml")
    event_listings = bs_obj.find('ul', class_='event-listings ').find_all('li', class_=False)
    for event in event_listings:
        artist_name = event.span.strong
        link = event.a['href']
        print artist_name
        print link

def main():
    location_entered_by_user = raw_input("Pleaser enter location: ")
    location_entered_by_user = location_entered_by_user.encode('utf-8')
    location_html = request_location(location_entered_by_user).text
    locations = parse_foundlocations(location_html)
    selected_location = choose_locations(locations)
    event_page = request_events(selected_location)
    parse_events(event_page.text)
    


     
     
if __name__ == '__main__':
    main()
