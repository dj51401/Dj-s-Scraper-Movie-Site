import requests
import pymongo
from multiprocessing import Process
from bs4 import BeautifulSoup

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["MovieDatabase"]
movieDB = database["movies"]

def ProcessLinks(urlList):
    if __name__ == "imdbscraper":
        procs = []

        for url in urlList:
            proc = Process(target=ScrapeIMDB, args=(url,))
            procs.append(proc)
            proc.start()
        
        for proc in procs:
            proc.join()

def ScrapeIMDB(url):    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    if(soup.find(id="title-overview-widget") != None):

        titleWrapperElement = soup.find("div", {"class": "title_wrapper"})        
        moviePoster = soup.find("div", {"class": "poster"}).findChild("a").findChild("img").get("src")
        movieImdbRating = soup.find("div", {"class": "ratingValue"}).find("span").text.strip()
        subtextElement = titleWrapperElement.findChild("div", {"class": "subtext"})
        titleElement = titleWrapperElement.find('h1', {"class": ""})
        movieName = titleElement.find(text=True, recursive=False).strip()
        movieReleaseYear = titleElement.find(id="titleYear").findChild('a').text.strip()
        movieRating = subtextElement.find(text=True, recursive=False).strip()
        movieRuntime = subtextElement.find("time").text.strip()
        movieSummary = soup.find("div", {"class": "summary_text"}).text.strip()

        movieReleaseDate = ''
        movieGenres = []

        genresList = subtextElement.findAll("a")
        for element in range(0, len(genresList)):
            if element != (len(genresList) - 1):
                movieGenres.append(genresList[element].text.strip())
            else:
                movieReleaseDate = genresList[element].text.strip()

        print("scraped: " + movieName)
        movieDB.update_one(
            {"_id" : movieName + movieReleaseYear},
            {
                "$set" : {
                    "_id" : movieName + movieReleaseYear,
                    "imdbLink": url,
                    "movieName": movieName,
                    "movieSummary": movieSummary,
                    "movieRelease": {
                        "movieReleaseYear": movieReleaseYear,
                        "movieReleaseDate": movieReleaseDate,
                    },
                    "movieGenre": movieGenres,
                    "movieRating": movieRating,
                    "movieRuntime": movieRuntime,
                    "movieImdbRating": movieImdbRating,
                    "movieSummary": movieSummary,
                    "moviePoster": moviePoster,
                }
            },
            upsert = True
        )