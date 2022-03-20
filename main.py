from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import requests
import urllib.request
import re


def fetch_youtube_link(movie):
    start_url = f"https://www.youtube.com/results?search_query={movie}" + "Trailer"
    url = start_url.replace(" ", "")
    video_ids = re.findall(r"watch\?v=(\S{11})",urllib.request.urlopen(url).read().decode())[0]
    youtube_link = f"https://www.youtube.com/watch?v={video_ids}"
    return youtube_link

def fetch_movies_info(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key=8265bd1679663a7ea12ac168da84d2e8&query={movie_title}"
    api_data = requests.get(url)
    api_data = api_data.json()
    rating = api_data['results'][0]['vote_average']
    release_date = api_data['results'][0]['release_date']
    release_date = release_date.split('-')[0]
    overview = api_data['results'][0]['overview'][:300]+"..."
    poster_path = "https://image.tmdb.org/t/p/w500/" + api_data['results'][0]['poster_path']
    return rating , release_date, overview, poster_path

def create_similarity():
    data = pd.read_csv('final_data_movies.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    similarity = cosine_similarity(count_matrix)
    return data, similarity


def rcmd(m):
    m = m.lower()
    data, similarity = create_similarity()
    if m not in data['movie_title'].unique():
        return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    else:
        i = data.loc[data['movie_title']==m].index[0]
        lst = list(enumerate(similarity[i]))
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
        lst = lst[1:6] # excluding first item since it is the requested movie itself
        title = []
        for i in range(len(lst)):
            a = lst[i][0]
            title.append(data['movie_title'][a])
        return title

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')
@app.route("/search", methods = ['POST'])
def index():
    if request.method == 'POST':
        searchstring = request.form['input']
        title = rcmd(searchstring)
        movies_recommended_info = []
        for i in title:
           movie_trailer = fetch_youtube_link(i)
           rating , release_date, overview, poster_path = fetch_movies_info(i)
           mydict = {"title": i,"movie_poster": poster_path ,"rating":rating,"release_date":release_date,"overview":overview,"movie_trailer":movie_trailer}
           movies_recommended_info.append(mydict)
        return render_template('try.html', movies_recommended_info = movies_recommended_info)


if __name__ == '__main__':
    app.run(debug=True)