import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from datetime import date

def get_current_date():
	today = date.today()
	return {
		"year": today.strftime("%Y"),
		"month": today.strftime("%B"),
		"day": today.strftime("%d").lstrip("0")
	}

def sanitize_input(date_as_tuple):
	sanitized_year = str(date_as_tuple[0])
	if not sanitized_year.isdigit():
		print("Error: non-digit characters in year. Using current year instead.")
		sanitized_year = get_current_date()['year']
	elif int(sanitized_year) < 2011 or int(sanitized_year) > 2030:
		print("Sorry, we don't have holiday info for that year. Using current year instead.")
		sanitized_year = get_current_date()['year']
	
	sanitized_month = date_as_tuple[1].title()
	if sanitized_month not in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
		print("Error: month not recognized. Using current month instead.")
		sanitized_month = get_current_date()['month']
	
	sanitized_day = str(date_as_tuple[2])
	if not sanitized_day.isdigit():
		print("Error: non-digit characters in day. Using current day instead.")
		sanitized_day = get_current_date()['day']
	elif int(sanitized_day) < 1 or int(sanitized_day) > 31:
		print("Error: incorrect day entered. Using current day instead.")
		sanitized_day = get_current_date()['day']

	return (sanitized_year, sanitized_month, sanitized_day)

def get_year_page(year):
	soup = BeautifulSoup(requests.get("http://www.interfaith-calendar.org/index.htm").text, "html.parser")
	links = soup.findAll("a")
	hrefs = []
	for link in links:
		hrefs.append(link.get("href"))

	# Get possible link format to year page
	year_option_1 = str(year) + ".htm"
	year_option_2 = str(year) + ".html"

	# Get link directly to current year page
	result = ""
	if year_option_1 in hrefs:
		result = year_option_1
	elif year_option_2 in hrefs:
		result = year_option_2

	return "http://www.interfaith-calendar.org/" + result

def get_month_data(month):
	pass

def clean_month_data(month_data):
	pass

def report_todays_holidays(today):
	pass

def check_calendar(year=get_current_date()['year'], month=get_current_date()['month'], day=get_current_date()['day']):
	year, month, day = sanitize_input((year, month, day))
	print(f"Today is {month} {day}, {year}.")

	year_page = get_year_page(year)
	print("year_page successfully found:")
	print(year_page)

	month_data = get_month_data(month)
	cleaned_month_data = clean_month_data(month_data)
	print(report_todays_holidays(cleaned_month_data))

# check_calendar()
check_calendar(2019,"december",31)

###