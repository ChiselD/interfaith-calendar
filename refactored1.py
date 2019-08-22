import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from datetime import date

# NOTES:
# Several months do not, and may never, work. Thank you, awful coder of this website >:O
# February refuses to print anything past the 10th.
# November refuses to print anything past the 24th.
# December refuses to print anything past the 12th.
# There's some messiness in check_calendar() and clean_month_data() about who calls what.
# TO DO: Print "Looks like today is not a holiday" message on non-holidays.

def get_current_date():
	# print("Running get_current_date()...")
	today = date.today()
	return {
		"year": today.strftime("%Y"),
		"month": today.strftime("%B"),
		"day": today.strftime("%d").lstrip("0")
	}

def sanitize_year(year):
	# print("Running sanitize_year()...")
	if not year.isdigit():
		print("Error: non-digit characters in year. Using current year instead.")
		return get_current_date()['year']
	elif int(year) < 2011 or int(year) > 2030:
		print("Sorry, we don't have holiday info for that year. Using current year instead.")
		return get_current_date()['year']
	else:
		return str(year)

def sanitize_month(month):
	# print("Running sanitize_month()...")
	if month.title() not in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
		print("Error: month not recognized. Using current month instead.")
		return get_current_date()['month']
	else:
		return month.title()

def sanitize_day(day):
	# print("Running sanitize_day()...")
	if not day.isdigit():
		print("Error: non-digit characters in day. Using current day instead.")
		return get_current_date()['day']
	elif int(day) < 1 or int(day) > 31:
		print("Error: incorrect day entered. Using current day instead.")
		return get_current_date()['day']
	else:
		return str(day)

def sanitize_input(date_as_tuple):
	# print("Running sanitize_input()...")
	return (sanitize_year(str(date_as_tuple[0])), sanitize_month(str(date_as_tuple[1])), sanitize_day(str(date_as_tuple[2])))

def get_correct_url_format(page_name, urls):
	# print("Running get_correct_url_format()...")
	option_1 = str(page_name) + ".htm"
	option_2 = str(page_name) + ".html"

	if option_1 in urls:
		return option_1
	elif option_2 in urls:
		return option_2
	else:
		return "N/A"

def get_year_page(year):
	# print("Running get_year_page()...")
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
	# print("Running find_month()...")
	for month in months:
		if re.search(month_to_find, str(month).lower()):
			return month
	else:
		return "N/A"

def get_month_data(year_url, month):
	# print("Running get_month_data()...")
	soup = BeautifulSoup(requests.get(year_url).text, "html.parser")
	h2s = soup.findAll("h2")[1:]
	month_regex = r"{}".format(month.lower())

	found_month_h2 = find_month(h2s, month_regex)

	# WARNING:
	# Things get hacky ahead, because the HTML DOM structure is weird :/
	# First we chain together next_sibling methods to get the sibling we want
	# Then we strip the last item, "Definitions", which we don't want
	if found_month_h2 == "N/A":
		print("Sorry, this month was not found.")
	else:
		return found_month_h2.next_sibling.next_sibling.contents[:-1]

def clean_date(problem_date):
	# print("Running clean_date()...")
	return "".join(c for c in problem_date if c.isdigit())

def multiday_list(data):
	# print("Running multiday_list()...")
	range_list = data.split("-")
	multiday = [str(n) for n in range(int(range_list[0]), int(range_list[1])+1)]
	return multiday

# The get_day_number function should always return a list, for consistency
def get_day_number(day_data):
	# print("Running get_day_number()...")
	day_number = str(day_data.contents[0].strip())

	if day_number.isdigit():
		return [day_number]
	
	# Check for equinox/solstice
	elif "Solstice" in day_number:
		return [clean_date(day_number), "the Solstice"]
	elif "Equinox" in day_number:
		return [clean_date(day_number), "the Equinox"]

	# One-off exception for Rosh Hashanah
	elif "October" in day_number:
		return [clean_date(day_number)[0:2], "Rosh Hashanah"]
	
	# Check for multiday holidays
	else: # TO DO: maybe turn this into "elif '-' in day_number" for readability
		return multiday_list(day_number)

def clean_month_data(month_data, today):
	# print("Running clean_month_data()...")
	# [0] holds day number, [1] holds holidays, [2] holds extra info
	current_holidays = [[], [], []]	
	# print("month_data is:")
	# print(month_data)
	for item in month_data:
		# Ignore all blank entries
		if str(type(item)) != "<class 'bs4.element.NavigableString'>":
		# if str(item) != "\n": # TO DO: might be able to replace line above with this line

			# Get each day number in order to check it against today's date
			day_number = get_day_number(item)
			if len(day_number) > 1 and day_number[1][0].isalpha():
				current_holidays[0] = day_number[0]
				current_holidays[2] = [day_number[1]]
			else:
				current_holidays[0] = day_number
				current_holidays[2] = []

			# Get holidays on this day
			todays_holidays = str(item.contents[1]).split("\n")

			current_holidays[1] = []
			for item in todays_holidays:
				if item != "<ul>" and item != "</ul>":
					text_to_append = unicodedata.normalize("NFKD", BeautifulSoup(item, "html.parser").get_text().strip())
					current_holidays[1].append(text_to_append)

		# print("current_holidays is now:")
		# print(current_holidays)

		if today in current_holidays[0]:
			# print("current_holidays[0] is now:")
			# print(current_holidays[0])
			report_todays_holidays(today, current_holidays)
			break

def report_todays_holidays(today, holidays):
	# print("Running report_todays_holidays()...")
	print("Today is a holiday!")
	if holidays[2]:
		print(f"Today is {holidays[2][0]}.")
	for holiday in holidays[1]:
		print(f"Today is {holiday}.")

def check_calendar(year=get_current_date()['year'], month=get_current_date()['month'], day=get_current_date()['day']):
	# print("Running check_calendar()...")
	year, month, day = sanitize_input((year, month, day))
	print(f"Today is {month} {day}, {year}.")

	year_url = get_year_page(year)

	month_data = get_month_data(year_url, month)

	cleaned_month_data = clean_month_data(month_data, day)
	# print(report_todays_holidays(cleaned_month_data))

# If you run check_calendar() with no arguments, it will default to today's date
check_calendar()
# check_calendar(2019,"august",15)

###