import pandas as pd
import os
from ast import literal_eval
from movie_recommender.apps import movie_data
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
def load_movie_data():
    df = movie_data
    return df


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
            names = [i['name'] for i in x]
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
    q_movies['genres'] =  q_movies['genres'].apply(literal_eval).apply(get_list)
    q_movies['runtime'] = q_movies['runtime'].apply(format_runtime)
    return  q_movies.to_dict('records')

def pre_process():
    df = movie_data
    features = ['cast', 'crew', 'keywords','genres','production_companies']
    for features in features:
        df[features] = df[features].apply(literal_eval)
    def get_director(x):
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan


    def get_list(x):
        if isinstance(x,list):
            names = [i['name'] for i in x]
            if len(names) > 3:
                names = names[:3]
            return names
        return []
    #cahnge it to lower case and remove the space
    def clean_data(x):
        if isinstance(x,list):
            return [str.lower(i.replace(" ","")) for i in x]
        else:
            if isinstance(x,str):
                return str.lower(x.replace(" ", ""))
            else: 
                return ' '

    def create_soup(x):
    
        return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres']) + ' ' + ' '.join(x['production_companies'])


            
    df['director'] = df['crew'].apply(get_director)
    df['director'] = df['director'].fillna('unknown')
    features = ['cast', 'keywords','genres','production_companies']
    for feature in features:
        df[feature] = df[feature].apply(get_list).apply(clean_data)
    df['soup'] = df.apply(create_soup,axis=1)
   
    return df

df = pre_process()
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df['soup'])
cosin_sim = cosine_similarity(count_matrix, count_matrix)

df = df.reset_index()
indices = pd.Series(df.index, index = df['title_x'])

def get_recommendation(title, cosine_sim = cosin_sim):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores,key = lambda x:x[1], reverse = True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return df[['title_x']].iloc[movie_indices]

    