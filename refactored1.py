import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from datetime import date

# NOTES:
# February does not, and may never, work. Thank you, awful coder of this website >:0
# November refuses to print anything past the 24th.
# December refuses to print anything past the 12th.

def get_current_date():
	today = date.today()
	return {
		"year": today.strftime("%Y"),
		"month": today.strftime("%B"),
		"day": today.strftime("%d").lstrip("0")
	}

def sanitize_year(year):
	if not year.isdigit():
		print("Error: non-digit characters in year. Using current year instead.")
		return get_current_date()['year']
	elif int(year) < 2011 or int(year) > 2030:
		print("Sorry, we don't have holiday info for that year. Using current year instead.")
		return get_current_date()['year']
	else:
		return str(year)

def sanitize_month(month):
	if month.title() not in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
		print("Error: month not recognized. Using current month instead.")
		return get_current_date()['month']
	else:
		return month.title()

def sanitize_day(day):
	if not day.isdigit():
		print("Error: non-digit characters in day. Using current day instead.")
		return get_current_date()['day']
	elif int(day) < 1 or int(day) > 31:
		print("Error: incorrect day entered. Using current day instead.")
		return get_current_date()['day']
	else:
		return str(day)

def sanitize_input(date_as_tuple):
	return (sanitize_year(str(date_as_tuple[0])), sanitize_month(str(date_as_tuple[1])), sanitize_day(str(date_as_tuple[2])))

def get_correct_url_format(page_name, urls):
	option_1 = str(page_name) + ".htm"
	option_2 = str(page_name) + ".html"

	if option_1 in urls:
		return option_1
	elif option_2 in urls:
		return option_2
	else:
		return "N/A"

def get_year_page(year):
	soup = BeautifulSoup(requests.get("http://www.interfaith-calendar.org/index.htm").text, "html.parser")
	links = soup.findAll("a")
	hrefs = []
	for link in links:
		hrefs.append(link.get("href"))

	found_page = get_correct_url_format(year, hrefs)
	if found_page == "N/A":
		print("Sorry, this year is not on the calendar.")
	else:
		return "http://www.interfaith-calendar.org/" + found_page

def find_month(months, month_to_find):
	for month in months:
		if re.search(month_to_find, str(month).lower()):
			return month
	else:
		return "N/A"

def get_month_data(year_url, month):
	soup = BeautifulSoup(requests.get(year_url).text, "html.parser")
	h2s = soup.findAll("h2")[1:]
	month_regex = r"{}".format(month.lower())

	found_month_h2 = find_month(h2s, month_regex)

	# WARNING:
	# Things get hacky ahead, because the HTML DOM structure is weird :/
	# First we string together next_sibling methods to get the sibling we want
	# Then we strip the last item, "Definitions", which we don't want
	if found_month_h2 == "N/A":
		print("Sorry, this month was not found.")
	else:
		return found_month_h2.next_sibling.next_sibling.contents[:-1]

def clean_date(problem_date):
	return "".join(c for c in problem_date if c.isdigit())

def multiday_list(data):
	range_list = data.split("-")
	multiday = []
	for n in range(int(range_list[0]), int(range_list[1])+1):
		multiday.append(str(n).split())
	return multiday

# The get_day_number function should always return a list, for consistency
def get_day_number(day_data):

	# day_number = str(day_data.contents[0].strip())
	day_number = str(day_data.contents[0].strip())

	if day_number.isdigit():
		return [day_number]
	
	# Check for equinox/solstice
	elif "Solstice" in day_number:
		return [clean_date(day_number), "Solstice"]
	elif "Equinox" in day_number:
		return [clean_date(day_number), "Equinox"]

	# One-off exception for Rosh Hashanah
	elif "October" in day_number:
		return [clean_date(day_number)[0:2], "Rosh Hashanah"]
	
	# Check for multiday holidays
	else:
		return multiday_list(day_number)

def clean_month_data(month_data):
	# [0] holds day number, [1] holds holidays, [2] holds extra info
	current_holidays = [[], [], []]	
	for item in month_data:
		# Ignore all blank entries
		if str(type(item)) != "<class 'bs4.element.NavigableString'>":
		# if str(item) != "\n": # Might be able to replace line above with this line; to test
			day_number = get_day_number(item)
			if len(day_number) > 1 and day_number[1][0].isalpha():
				current_holidays[0] = day_number[0]
				current_holidays[2] = day_number[1]
			else:
				current_holidays[0] = day_number
		# print("current_holidays is now:")
		# print(current_holidays)

def report_todays_holidays(today):
	pass

def check_calendar(year=get_current_date()['year'], month=get_current_date()['month'], day=get_current_date()['day']):
	year, month, day = sanitize_input((year, month, day))
	print(f"Today is {month} {day}, {year}.")

	year_url = get_year_page(year)
	print("year_url successfully found:")
	print(year_url)

	month_data = get_month_data(year_url, month)
	print("month_data successfully found:")
	print(month_data)

	cleaned_month_data = clean_month_data(month_data)
	print(report_todays_holidays(cleaned_month_data))

# check_calendar()
check_calendar(2019,"june",21)

###