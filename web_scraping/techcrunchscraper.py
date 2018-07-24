from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import requests
from requests.exceptions import RequestException
import csv
import datetime

try:

    url = "https://techcrunch.com/"

    top_story_titles = set()
    time = datetime.datetime.now()

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    for article in soup.find_all('div', class_="post-block post-block--image post-block--unread"):
        for links in article.find_all('a', limit=2):
            print(links.text.strip())
        for date in article.find('time'):
            print(date.string.strip())
        for i in article.find_all('img'):
            print(i['src'])
            img_url = i['src']
            img = Image.open(BytesIO(requests.get(img_url).content))
            img.show()

        print()
    '''
    for a in soup.find_all("a", class_="link-gray"):
        child = a.find("h2")
        top_story_titles.add(child.text)

    with open("buzzfeednews.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Top Buzzfeed Stories as of {}".format(str(time))])
        for title in top_story_titles:
            writer.writerow([title])
        f.close()
'''
except RequestException as e:
    print('Error during requests to {0} : {1}'.format(url, str(e)))



















