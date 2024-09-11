
from ast import literal_eval
import numpy as np
"""
def load_movie_data():
    df = movie_data
    return df

"""


def pre_process(df):
    df = df
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