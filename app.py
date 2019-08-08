import requests
from bs4 import BeautifulSoup
from datetime import date
import re

### GO TO CURRENT YEAR PAGE ###

# Get current date info

today = date.today()
current_year = today.strftime("%Y")
current_month = today.strftime("%B")
current_day = today.strftime("%d").lstrip("0")

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
	print("Year found: " + year_url)


### COLLECT HOLIDAYS ###

year_response = requests.get(year_url)
year_html = year_response.text
year_soup = BeautifulSoup(year_html, "html.parser")

h2s = year_soup.findAll("h2")
month_regex = r"{}".format(current_month.lower())

def find_month(months, month_to_find):
	for month in months:
		if re.search(month_to_find, str(month).lower()):
			print("Found!")
			return month
	else:
		return "N/A"

current_month_h2 = find_month(h2s, month_regex)
print("Type of current_month_h2 is:")
print(type(current_month_h2))

print(current_month_h2)
print("Next element is...")
print(current_month_h2.next_element)

print("Type of current_month_h2.next_element is:")
print(type(current_month_h2.next_element))

all_holidays_this_month = ""