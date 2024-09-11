from django.apps import AppConfig
import pandas as pd
import os

class MovieRecommenderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movie_recommender"
    
    def ready(self):
        global movie_data
        csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'tmdb_movie_metadata_with_posters_cleaned.csv')
        movie_data = pd.read_csv(csv_file_path)
