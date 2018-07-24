from bs4 import BeautifulSoup
import urllib.request
from requests.exceptions import RequestException
import csv
import datetime

'''
Notes:
- check for duplicate articles (one could appear in multiple categories)
- different subsections:
	- community
	- giftguide
	- investigations
	- asis (same thing as style) - ugh this looks annoying, skipped

'''
class Article:

	def __init__(self, url_ext, title, subtitle, author):
		"""Return an Article object whose url extension is *url_ext*,
		title is *title*, subtitle is *subtitle*, and author is *author*"""
		self.url_ext = url_ext
		self.title = title
		self.subtitle = subtitle
		self.author = author 

	def __repr__(self):
		return self.title + '\n' +  self.subtitle + '\n'+ self.author + '\n' + self.url_ext

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.url_ext == other.url_ext and self.title == other.title and self.subtitle == other.subtitle and self.author == other.author
		else:
			return False


def scrape_articles(soup):
	"""Return a list of Article objects scraped by a BeautifulSoup object *soup*
	from sections of the Buzzfeed website that follows a generic HTML structure"""
	articles = []
	#get feature article data:
	feature_div = soup.find("div", class_="featured-card__body")
	feature_url = feature_div.find("a")['href']
	feature_title = feature_div.find("h1").text.strip()
	feature_subtitle = feature_div.find("p").text.strip()
	feature_author = feature_div.find("span").text.strip()
	feature_article = Article(feature_url, feature_title, feature_subtitle, feature_author)
	articles.append(feature_article)

	for ar in soup.find_all("div", class_="story-card"):
		url = ar.find("a")['href']
		title = ar.find("h2").text.strip()
		subtitle = ar.find("p").text.strip()
		author = ar.find("span").text.strip()
		articles.append(Article(url, title, subtitle, author))

	return articles

def uniquely_add(existing, new):
	"""Adds a list of Articles *new* to an existing list of articles *existing*
	such that no duplicate Articles are appended to *existing*"""
	for a in new:
		if not a in existing:
			existing.append(a)

def scrape_main_page(soup):
	"""Return a list of Article objects scraped by a BeautifulSoup object *soup*
	from Buzzfeed homepage"""
	articles = []
	#get feature article data:
	feature_div = soup.find("div", class_="featured-package card")
	feature_url = feature_div.find("a")['href']
	feature_title = feature_div.find("h1").text.strip()
	feature_subtitle = feature_div.find("p").text.strip()
	feature_author = feature_div.find("span").text.strip()
	feature_article = Article(feature_url, feature_title, feature_subtitle, feature_author)
	articles.append(feature_article)

	for ar in soup.find_all("div", class_="card story-card xs-relative xs-mb05 md-mb1 xs-border-left-none xs-border-right-none md-border-lighter js-feed-item"):
		url = ar.find("a")['href']
		title = ar.find("h2").text.strip()
		subtitle = ar.find("p").text.strip()
		author = ar.find("span").text.strip()
		articles.append(Article(url, title, subtitle, author))

	return articles

def scrape_community(soup):
	"""Return a list of Article objects scraped by a BeautifulSoup object *soup*
	from Buzzfeed community page"""
	articles = []
	#get feature article data:
	feature_div = soup.find("div", class_="featured-card__body")
	feature_url = feature_div.find("a")['href']
	feature_title = feature_div.find("h1").text.strip()
	feature_subtitle = feature_div.find("p").text.strip()
	feature_author = feature_div.find("span").text.strip()
	feature_article = Article(feature_url, feature_title, feature_subtitle, feature_author)
	articles.append(feature_article)

	for ar in soup.find_all("div", class_="card story-card xs-relative xs-mb05 md-mb1 xs-border-left-none xs-border-right-none md-border-lighter js-feed-item"):
		url = ar.find("a")['href']
		title = ar.find("h2").text.strip()
		subtitle = ar.find("p").text.strip()
		author = ar.find("span").text.strip()
		articles.append(Article(url, title, subtitle, author))

	return articles

def scrape_giftguide(soup):
	"""Return a list of Article objects scraped by a BeautifulSoup object *soup*
	from Buzzfeed gift guide page"""
	articles = []

	for a in soup.find_all("a", class_="link-gray"):
		url = a['href']
		title = a.find("div", class_="xs-text-4 md-text-2 bold xs-mb05 xs-pt05 md-px05").text.strip()
		subtitle = a.find("div", class_="xs-hide sm-block xs-text-4 text-gray-lighter xs-mb3 md-mr1 md-px05").text.strip()
		author = "none"
		articles.append(Article(url, title, subtitle, author))

	return articles

try:
	articles = []
	base_url = "http://www.buzzfeed.com"
	url_extensions = ["animals", "books", "business", "buzz", "celebrity", "entertainment", 
					"food", "health", "lgbt", "life", "music", "nifty", "parents", 
					"politics", "reader", "rewind", "science", "shopping", "trending", "tech", 
					"travel", "weddings", "world"]
	different_extensions = ["", "community", "giftguide", "investigations", "news", "quizzes"]
	top_story_titles = set()
	time = datetime.datetime.now()

	# for ext in url_extensions:
	# 	print(ext)
	# 	full_url = base_url + "/" + ext
	# 	wp = urllib.request.urlopen(full_url)
	# 	page = wp.read()
	# 	soup = BeautifulSoup(page, "html.parser")
	# 	uniquely_add(articles, scrape_articles(soup))

	for ext in different_extensions:
		print(ext)
		full_url = base_url + "/" + ext
		wp = urllib.request.urlopen(full_url)
		page = wp.read()
		soup = BeautifulSoup(page, "html.parser")
		if ext == "":
			pass #uniquely_add(articles, scrape_main_page(soup))
		elif ext == "community":
			pass #uniquely_add(articles, scrape_community(soup))
		elif ext == "giftguide":
			uniquely_add(articles, scrape_giftguide(soup))
		elif ext == "investigations":
			break
		elif ext == "news":
			break
		elif ext == "quizzes":
			break

	print(len(articles))
	with open("buzzfeedarticles.csv", 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["Top Buzzfeed Stories as of {}".format(str(time))])
		for article in articles:
			writer.writerow([article])
		f.close()

except RequestException as e:
	print('Error during requests to {0} : {1}'.format(base_url, str(e)))

