import requests
import pymongo
import imdbscraper
from bs4 import BeautifulSoup;

client = pymongo.MongoClient("mongodb://localhost:27017")
movieDatabase = client["MovieDatabase"]
movieDB = movieDatabase["movies"]

url = "http://www.imdb.com/search/title/?title_type=feature&year=1950-01-01,2020-12-31&sort=num_votes,desc&start=5051"
def sendLinks(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    listerItem = soup.findAll("div", {"class" : "lister-item"})

    for i in range(len(listerItem)):
        listLink = listerItem[i].find("div", {"class" : "lister-item-image"}).findChild("a").get("href")
        print("Scraping: http://www.imdb.com" + listLink)
        imdbscraper.ScrapeIMDB("http://www.imdb.com" + listLink)

    nextPage = soup.find("div", {"class" : "desc"}).findChild("a", {"class" : "next-page"})
    print("Going to next page: http://www.imdb.com" + nextPage.get("href"))
    sendLinks("http://www.imdb.com" + nextPage.get("href"))


sendLinks(url)