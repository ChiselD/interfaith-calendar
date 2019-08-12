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
		# "month": "February",
		"day": today.strftime("%d").lstrip("0")
		# "day": "1"
	}

def check_calendar():
	current = get_current_date()
	print("current['year'] is: " + current['year'])
	print("current['month'] is: " + current['month'])
	print("current['day'] is: " + current['day'])
	# year_page = get_year_page()
	# get_current_month_data()

check_calendar()