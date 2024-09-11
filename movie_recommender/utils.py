import pandas as pd
import os
from ast import literal_eval
import numpy as np
from django.core.cache import cache
from io import StringIO



def calculate_scores(df):
    c = df['vote_average'].mean()

    m = df['vote_count'].quantile(0.9)

    q_movies = df.copy().loc[df['vote_count'] >= m]
    def weighted_rating(x, m=m,c=c):
        v = x['vote_count']
        r = x['vote_average']

        return (v/(v + m) * r ) + (m/(m + v) * c)
    def get_list(x):
        if isinstance(x,list):
            names = [i['name'] for i in x if isinstance(i,dict)]

            if len(names) > 3:
                names = names[:3]
            return names
        return []
    def format_runtime(minutes):
        if pd.notna(minutes):
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}h {minutes}m"
        return "N/A"
   
    q_movies['score'] = q_movies.apply(weighted_rating,axis=1)
    q_movies = q_movies.sort_values('score', ascending = False)
    if q_movies['genres'].dtype == object:
        q_movies['genres'] = q_movies['genres'].apply(lambda x: literal_eval(x) if isinstance(x, str) else x)
    q_movies['genres'] =  q_movies['genres'].apply(get_list)
    q_movies['runtime'] = q_movies['runtime'].apply(format_runtime)
    return  q_movies.to_dict('records')


"""
df = pre_process()
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df['soup'])
cosin_sim = cosine_similarity(count_matrix, count_matrix)

df = df.reset_index()
indices = pd.Series(df.index, index = df['title_x'])
"""

def get_recommendation(df,indices, title, cosine_sim):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores,key = lambda x:x[1], reverse = True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return df[['title_x','id','poster_url']].iloc[movie_indices]

def get_cached_data():
        movie_data_json = cache.get('movie_data')
        if movie_data_json is not None:
            movie_data = pd.read_json(StringIO(movie_data_json))
            return movie_data
        else:
            return None
        