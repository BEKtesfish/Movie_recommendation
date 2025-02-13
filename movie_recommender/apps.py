from django.apps import AppConfig
import pandas as pd
import os
from .data_preprocess import pre_process
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache

class MovieRecommenderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movie_recommender"
    
    def ready(self):
        try:
        
            csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'tmdb_movie_metadata_with_posters_cleaned.csv')
            movie_data = pd.read_csv(csv_file_path)

            processed_df = pre_process(movie_data)
            count_matrix = CountVectorizer(stop_words='english').fit_transform(processed_df['soup'])
            cosine_sim = cosine_similarity(count_matrix, count_matrix)
            df = processed_df.reset_index()
            indices = pd.Series(df.index, index = df['title_x'])
            
            movie_data_json = movie_data.to_json()
            cache.set('movie_data',movie_data_json, timeout=None)
            cache.set('cosine_sim', cosine_sim,timeout=None)
            #cache.set('indices', indices)
        except Exception as e:
            print(f"Error during app initialization: {e}")