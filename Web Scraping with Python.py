from gazpacho import Soup
import requests
import pandas as pd

url = "https://www.imdb.com/search/title/?groups=top_100&sort=user_rating,desc"
html = requests.get(url)

imdb = Soup(html.text)
titles = imdb.find("h3", {"class": "lister-item-header"})
ratings = imdb.find("div", {"class": "inline-block ratings-imdb-rating"})

n = len(titles)

nums = [i+1 for i in range(n)]
clean_titles = [title.strip()[3:-7].lstrip() for title in titles]
clean_years = [title.strip()[-5:-1] for title in titles]
clean_ratings = [float(rating.strip()) for rating in ratings]

movies = pd.DataFrame({
    "title": clean_titles,
    "year": clean_years,
    "rating": clean_ratings
}, index = nums)

movies
