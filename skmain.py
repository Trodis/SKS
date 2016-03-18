# -*- coding: utf-8 -*-
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

def request_concertpage(concert_link):
    url = "https://songkick.com%s" %concert_link
    concert_page = requests.get(url)
    return concert_page

def parse_concertpage(concert_page, artist_name):
    bs_obj = BeautifulSoup(concert_page.text, "lxml")
    tickets_table = bs_obj.find('div', id='tickets')
    tickets_list = []
    for tickets in tickets_table.find_all('div', class_='ticket-wrapper'):
        for cell in tickets.find_all('div'):
            print artist_name
            print cell
        
        print "******************"

def parse_events(event_page):
    bs_obj = BeautifulSoup(event_page, "lxml")
    event_listings = bs_obj.find('ul', class_='event-listings ').find_all('li', class_=False)
    for event in event_listings:
        if event.span.strong and event.a['href']:
            artist_name = event.span.strong
            link = event.a['href']
            concert_page = request_concertpage(link)
            parse_concertpage(concert_page, artist_name)
        else:
            continue

def main():
    location_entered_by_user = raw_input("Pleaser enter location: ")
    location_entered_by_user = location_entered_by_user.decode('utf-8')
    location_html = request_location(location_entered_by_user).text
    locations = parse_foundlocations(location_html)
    selected_location = choose_locations(locations)
    event_page = request_events(selected_location)
    parse_events(event_page.text)
    

if __name__ == '__main__':
    main()
