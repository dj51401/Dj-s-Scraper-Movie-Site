import requests
import pymongo
from bs4 import BeautifulSoup

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["MovieDatabase"]
movieDB = database["movies"]

def ScrapeIMDB(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    titleWrapperElement = soup.find("div", {"class": "title_wrapper"})        
    moviePoster = soup.find("div", {"class": "poster"}).findChild("a").findChild("img").get("src")
    movieImdbRating = soup.find("div", {"class": "ratingValue"}).find("span").text.strip()
    subtextElement = titleWrapperElement.findChild("div", {"class": "subtext"})
    titleElement = titleWrapperElement.find('h1', {"class": ""})

    if(titleElement != None):
        movieName = titleElement.find(text=True, recursive=False).strip()
        movieReleaseYear = titleElement.find(id="titleYear").findChild('a').text.strip()

        movieRating = subtextElement.find(text=True, recursive=False).strip()
        movieRuntime = subtextElement.find("time").text.strip()

        movieReleaseDate = ''
        movieGenres = []

        genresList = subtextElement.findAll("a")
        for element in range(0, len(genresList)):
            if element != (len(genresList) - 1):
                movieGenres.append(genresList[element].text.strip())
            else:
                movieReleaseDate = genresList[element].text.strip()

        movieSummary = soup.find("div", {"class": "summary_text"}).text.strip()
    

        movieDB.update_one(
            {"movieName" : movieName},
            {
                "$set" : {
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