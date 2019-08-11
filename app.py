import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from datetime import date

# OUTSTANDING ISSUES:
# all dates (weirdly slow)
# September, all dates (source page layout: presence of word "October" in date field)
# October 20 (text encoding issue)
# February, all dates (IndexError: list index out of range)
# March, various (missing Nineteen Day Fast)
# March 21 (text encoding issue)
# May, all dates (getting "No holiday today" message)
# - for May: probably deleted wrong alternates when deleting blanks
# June 5-7 (missing multiday holidays)
# November 28 (getting "No holiday today" message)
# December, various (not getting any holiday messages)
# - for December: probably deleted wrong alternates when deleting blanks

### GO TO CURRENT YEAR PAGE ###

# Get current date info

today = date.today()
current_year = today.strftime("%Y")
# current_month = today.strftime("%B")
current_month = "June"
# current_day = today.strftime("%d").lstrip("0")
current_day = "21"

print(f"Today is {current_month} {current_day}, {current_year}.")

# Get list of years available on calendar

root_url = "http://www.interfaith-calendar.org/index.htm"

root_response = requests.get(root_url)
root_html = root_response.text
root_soup = BeautifulSoup(root_html, "html.parser")

root_links = root_soup.findAll("a")
root_hrefs = []
for link in root_links:
	root_hrefs.append(link.get("href"))

def find_current_year_page(arr):
	# Get possible link format to year page
	year_option_1 = str(current_year) + ".htm"
	year_option_2 = str(current_year) + ".html"

	# Get link directly to current year page
	if year_option_1 in arr:
		return year_option_1
	elif year_option_2 in arr:
		return year_option_2
	else:
		return "N/A"

result = find_current_year_page(root_hrefs)
if result == "N/A":
	print("Sorry, this year is not on the calendar.")
else:
	year_url = "http://www.interfaith-calendar.org/" + result
	# print("Year found: " + year_url)


### COLLECT ALL HOLIDAYS ###

year_response = requests.get(year_url)
year_html = year_response.text
year_soup = BeautifulSoup(year_html, "html.parser")

h2s = year_soup.findAll("h2")
month_regex = r"{}".format(current_month.lower())

def find_month(months, month_to_find):
	for month in months:
		if re.search(month_to_find, str(month).lower()):
			return month
	else:
		return "N/A"

current_month_h2 = find_month(h2s, month_regex)

# WARNING:
# Things get hacky ahead, because the HTML DOM structure is weird :/
# First we string together next_sibling methods to get the sibling we want
# Then we strip the last item, "Definitions", which we don't want
holiday_data = current_month_h2.next_sibling.next_sibling.contents[:-1]

# Function to remove all non-numeric chars from date strings (e.g. in equinoxes/solstices)
def clean_date(problem_date):
	return "".join(c for c in problem_date if c.isdigit())

# Function to break down multi-day info and append all those days to a list
def multiday_list(data):
	range_list = data.split("-")
	multiday = []
	for n in range(int(range_list[0]), int(range_list[1])+1):
		multiday.append(str(n).split())
	return multiday

# Put all holiday days this month in a list
holiday_days_this_month = []

# Each holiday_data_item contains 1. date, 2. holidays (w/ HTML), and optionally 3. blankness
for holiday_data_item in holiday_data:
	if holiday_data.index(holiday_data_item) % 2 == 1: # Alternating items are blank, for some reason, so this line skips them

		# [0] holds day number, [1] holds holidays, [2] holds equinox/solstice info
		current_holidays = [[], [], []]

		# Get day and append it to current_holiday
		day_number = str(holiday_data_item.contents[0].strip())
		if day_number.isdigit():
			current_holidays[0].append(day_number)
		# Check for equinox/solstice
		elif "Solstice" in day_number:
			current_holidays[0].append(clean_date(day_number))
			current_holidays[2].append("Solstice")
		elif "Equinox" in day_number:
			current_holidays[0].append(clean_date(day_number))
			current_holidays[2].append("Equinox")
		# Check for multiday holidays
		else:
			multiday = True
			current_holidays[0] = multiday_list(day_number)

		# Get holidays on this day
		todays_holidays = str(holiday_data_item.contents[1]).split("\n")

		for item in todays_holidays:
			if item != "<ul>" and item != "</ul>":
				text_to_append = unicodedata.normalize("NFKD", BeautifulSoup(item, "html.parser").get_text().strip())
				current_holidays[1].append(text_to_append)

		holiday_days_this_month.append(current_holidays)


### CHECK IF TODAY IS A HOLIDAY ###

is_today_a_holiday = False
success_message_printed = False

for day in holiday_days_this_month:
	if current_day in day[0]:
		is_today_a_holiday = True
		if day[2]:
			print(f"Today is the {day[2][0]}.")
		if success_message_printed == False:
			print("Today is a holiday!")
			success_message_printed = True
		for holiday in day[1]:
			print(holiday)
		if len(day[0]) > 1:
			print(f"(The holiday above lasts from {current_month} {day[0][0]} to {current_month} {day[0][-1]}.)")

if is_today_a_holiday == False:
	print("I know of no major holidays on this date.")


#################################################