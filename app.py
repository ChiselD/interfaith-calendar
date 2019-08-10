import requests
from bs4 import BeautifulSoup
from datetime import date
import re

### GO TO CURRENT YEAR PAGE ###

# Get current date info

today = date.today()
current_year = today.strftime("%Y")
current_month = today.strftime("%B")
# current_day = today.strftime("%d").lstrip("0")
current_day = "10"

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
# First we string together next_sibling methods to get to the sibling we want
# Then we strip the last item, "Definitions", which we don't want
holiday_data = current_month_h2.next_sibling.next_sibling.contents[:-1]

# Function to break down multi-day info and append all those days to a list
def append_multiple_days(arr, data):
	range_list = data.split("-")
	for n in range(int(range_list[0]), int(range_list[1])+1):
		arr.append(str(n))

# Put all holiday days this month in a list
holiday_days_this_month_with_duplicates = []
# Each holiday_data_item contains 1. date, 2. holidays (w/ HTML), and optionally 3. blankness
for holiday_data_item in holiday_data:
	if holiday_data.index(holiday_data_item) % 2 == 1: # Alternating items are blank, for some reason, so this line skips blanks

		print("Length of holiday_data_item after removing blanks: ")
		print(len(holiday_data_item))
		print("All remaining contents of holiday_data_item after removing blanks:")
		for content in holiday_data_item.contents:
			print("Content: ")
			print(content)

		holidays_today = []

		# Get day and append it to holidays_today
		day_number = holiday_data_item.contents[0].strip()
		if day_number.isdigit():
			holiday_days_this_month_with_duplicates.append(day_number)
		else:
			multiday = True
			append_multiple_days(holiday_days_this_month_with_duplicates, day_number)

		# Get holiday info and append it to holidays_today
		holidays_today.append(holiday_data_item.contents[1].get_text().strip()) # type: bs4.element.Tag

# Remove duplicate day values while preserving order
holiday_days_this_month = list(dict.fromkeys(holiday_days_this_month_with_duplicates))
print("All holiday days this month:")
print(holiday_days_this_month)

# Function to list all the holidays that occur on a certain day
# def list_todays_holidays(day):
# 	pass

# Check if there is a holiday today
if current_day in holiday_days_this_month:
	print("There's a holiday today!")
	# list_todays_holidays(current_day)
else:
	print("There are no major holidays today.")


holidays_today = [] # All plaintext holidays occurring today will go in this list
for html_item in holidays_today_raw.contents:
	if html_item != "\n":
		holidays_today.append(html_item.get_text().strip())
print("RESULTS:")
for holiday in holidays_today:
	print(holiday)
print("\n")

def report_todays_holidays(holidays):
	print(f"Today is {current_month} {current_day}, {current_year}.")
	for holiday in holidays:
		print("Today is: " + holiday)

report_todays_holidays(holidays_today)


#################################################