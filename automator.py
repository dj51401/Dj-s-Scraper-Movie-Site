import requests
import pymongo
import imdbscraper
from multiprocessing import Process
from bs4 import BeautifulSoup;

client = pymongo.MongoClient("mongodb://localhost:27017")
movieDatabase = client["MovieDatabase"]
movieDB = movieDatabase["movies"]
nextPage = ""
url = "http://www.imdb.com/search/title/?title_type=feature&year=1950-01-01,2020-12-31&sort=num_votes,desc&start=1"
work = []

#Sends links of individual movies to imdbscraper from a list of movies

def sendLinks(url):
    work.clear()
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    nextPageURL = soup.find("div", {"class" : "desc"}).findChild("a", {"class" : "next-page"}).get("href")
    movieListElement = soup.findAll("div", {"class" : "lister-item"})
    getWork(movieListElement)
    procs = []

    for url in work:
        proc = Process(target=imdbscraper.ScrapeIMDB, args=[url])
        procs.append(proc)
        proc.start()   

    for proc in procs:
        proc.join()

    sendLinks("http://www.imdb.com" + nextPageURL)

def getWork(listerItem):
    for i in range(len(listerItem)):
        listLink = listerItem[i].find("div", {"class" : "lister-item-image"}).findChild("a").get("href")
        work.append("http://www.imdb.com" + listLink)

if(__name__ == "__main__"):
    sendLinks(url)