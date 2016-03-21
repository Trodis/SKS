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
    tickets_list = []
    tickets_table = bs_obj.find('div', id='tickets')
    for tickets in tickets_table.find_all('div', class_='ticket-wrapper'):
        ticket_wrapper = tickets.find_all('div')
        if ticket_wrapper[1].span is not None:
            vendor = ticket_wrapper[0].span.text
            ticket_price = ticket_wrapper[1].span.text
            ticket_link = tickets.a['href']
            tickets_list.append({'vendor':vendor, 'price': ticket_price, 'link': ticket_link})
        else:
            continue

    address = []
    venue_hcard = bs_obj.find('p', class_='venue-hcard').find_all('span')
    for a in venue_hcard:
        address.append(a.text)

    additional_details = bs_obj.find('div', class_='additional-details-container')
    if additional_details is not None:
        additional_details = additional_details.p.text
    else:
        additional_details = False

    return tickets_list, address, additional_details

def write_sheet(artist_name, tickets, address, details, wb, ws):
    row_number = ws.max_row+1
    ws.cell(row=row_number, column=1, value=event_name)
    ws.cell(row=row_number, column=2, value=event_facebook_url)
    ws.cell(row=row_number, column=3, value=date_start)
    ws.cell(row=row_number, column=4, value=ticket_uri)
    ws.cell(row=row_number, column=5, value=city)
    ws.cell(row=row_number, column=6, value=interested_count)
    ws.cell(row=row_number, column=7, value=attending_count)
    wb.save(EXCELFILE) 

def create_sheet():
    wb = Workbook()
    ws = wb.active
    ws.cell(row=1, column=1, value='Name').font = Font(bold=True)
    ws.cell(row=1, column=2, value='Songkick URL').font = Font(bold=True)
    ws.cell(row=1, column=3, value='Date Start').font = Font(bold=True)
    ws.cell(row=1, column=4, value='Ticket Link').font = Font(bold=True)
    ws.cell(row=1, column=5, value='City').font = Font(bold=True)
    ws.cell(row=1, column=6, value='Address').font = Font(bold=True)
    ws.cell(row=1, column=7, value='Additional Details').font = Font(bold=True)
    wb.save(EXCELFILE)

    return wb, ws 

def parse_events(event_page):
    bs_obj = BeautifulSoup(event_page, "lxml")
    event_listings = bs_obj.find('ul', class_='event-listings ').find_all('li', class_=False)
    for event in event_listings:
        if event.span.strong and event.a['href']:
            artist_name = event.span.strong
            link = event.a['href']
            concert_page = request_concertpage(link)
            tickets, address, details = parse_concertpage(concert_page, artist_name)
            save_scraped(artist_name, tickets, address, details)
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
