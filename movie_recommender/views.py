from django.shortcuts import render
from  .utils import load_movie_data, calculate_scores, get_recommendation
from django.core.paginator import  Paginator
import pandas as pd

# Create your views here.

def home(request):
    df = load_movie_data()
    top_movies = pd.DataFrame(calculate_scores(df))
    movies_dict = top_movies.to_dict(orient = 'records')

    paginator = Paginator(movies_dict, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    ctx = {'movies': page_obj}
    return render(request, 'movie_recommender/home.html', ctx)

def details(request,id):
    df = load_movie_data()
    movie = df[id]
