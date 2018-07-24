from bs4 import BeautifulSoup
import urllib.request
from requests.exceptions import RequestException
import csv
import datetime

try:

	url = "http://www.buzzfeed.com"

	top_story_titles = set()
	repeat_scrapes = 5
	time = datetime.datetime.now()

	for i in range(repeat_scrapes):

		wp = urllib.request.urlopen(url)
		page = wp.read()
		soup = BeautifulSoup(page, "html.parser")

		for a in soup.find_all("a", class_="link-gray"):
			child = a.find("h2")
			top_story_titles.add(child.text)

	with open("buzzfeedhtml.txt",'w') as html_file:
		html_file.write(str(soup))
		html_file.close()

	with open("buzzfeednews.csv", 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["Top Buzzfeed Stories as of {}".format(str(time))])
		for title in top_story_titles:
			writer.writerow([title])
		f.close()

except RequestException as e:
	print('Error during requests to {0} : {1}'.format(url, str(e)))

