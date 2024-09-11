from django.shortcuts import render
from  .utils import calculate_scores, get_recommendation,get_cached_data
from django.core.paginator import  Paginator
import pandas as pd
import os
from ast import literal_eval
from django.core.cache import cache
from django.conf import settings
# Create your views here.


def home(request):
    """
    df = cache.get('movie_data')
    if df is None:
        return render(request, 'movie_recommender/home.html', {'error': 'Data not available'})
    """
    df = get_cached_data()
    if df is None:
        csv_file_path = os.path.join(settings.BASE_DIR, 'movie_recommender', 'data', 'tmdb_movie_metadata_with_posters_cleaned.csv')
        df = pd.read_csv(csv_file_path)
    top_movies = pd.DataFrame(calculate_scores(df))
    movies_dict = top_movies.to_dict(orient = 'records')

    paginator = Paginator(movies_dict, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    ctx = {'movies': page_obj}
    return render(request, 'movie_recommender/home.html', ctx)

def details(request,id):
    def get_list(x):
        if isinstance(x,list):
            names = [i['name'] for i in x  if isinstance(i,dict)]
            if len(names) > 3:
                names = names[:3]
            return names
        return []
    features = ['genres','production_companies', 'cast']
    df = get_cached_data()
    if df is None:
        csv_file_path = os.path.join(settings.BASE_DIR, 'movie_recommender', 'data', 'tmdb_movie_metadata_with_posters_cleaned.csv')
        df = pd.read_csv(csv_file_path)

    cosine_sim= cache.get('cosine_sim')
    
    #indices = cache.get('indices')

    if df is None:
        return render(request, 'movie_recommender/home.html', {'error': 'Data not available'})
    for feature in features:
        if df[feature].dtype == object:
            df[feature] = df[feature].apply(lambda x: literal_eval(x) if isinstance(x, str) else x)
        df[feature].apply(get_list)
    print(f"len= {df.shape}")
    movie = df[df['id']== id]
    movies_details = movie.iloc[0]
    df =df.reset_index()
    indices=pd.Series(df.index, index=df['title_x'])
    print(f"indices = {indices}")
    recommendations = get_recommendation(df,indices,movies_details['title_x'], cosine_sim)
    recommendations['id'] = pd.to_numeric(recommendations['id'], errors='coerce').astype('Int64')  # Convert to integer
    recommendations['title_x'] = recommendations['title_x'].astype(str)  # Convert to string
    print(f"recommendations= {recommendations}")
    print(f"movies_details = {movies_details }")

    #recommendations['movie_id'] = movie_indices
    #zipped_recommendations = list(zip(recommendations, movie_indices))

    ctx = {
        'movie': movies_details ,
        'recommendations': recommendations.to_dict(orient='records') 
    }
      
    return render(request,'movie_recommender/movie_detail.html', ctx)

def movie_search(request):
    """
    df = cache.get('movie_data')
    if df is None:
        return render(request, 'movie_recommender/home.html', {'error': 'Data not available'})
    """
    cosine_sim= cache.get('cosine_sim')
    query =request.GET.get('q')
    df = get_cached_data()

    if df is None:
        csv_file_path = os.path.join(settings.BASE_DIR, 'movie_recommender', 'data', 'tmdb_movie_metadata_with_posters_cleaned.csv')
        df = pd.read_csv(csv_file_path)
    results = []
    if query:
        filtered_df = df[df['title_x'].str.contains(query, case=False, na=False) | df['genres'].str.contains(query, case=False, na=False)]
        results = filtered_df.to_dict(orient = 'records')
    
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    recommendations = []
    if results:
        first_movie = results[0]
        movie_title = first_movie['title_x']
        df = df.reset_index()
        indices = pd.Series(df.index, index=df['title_x'])
        
        recommendations = get_recommendation(df, indices, movie_title, cosine_sim)
        recommendations['id'] = pd.to_numeric(recommendations['id'], errors = 'coerce').astype('Int64')  # Convert to integer
        recommendations['title_x'] = recommendations['title_x'].astype(str)  # Convert to string

    ctx = {'movies': page_obj,
           'query': query,
           'recommendations': recommendations.to_dict(orient='records'),
           }
    return render(request, 'movie_recommender/movie_search.html', ctx)