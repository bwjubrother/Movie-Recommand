from django.shortcuts import render,redirect, get_object_or_404
import requests
from .models import Movie, Comment, Score, Review
from .forms import MovieForm, CommentForm, ReviewForm, SearchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db.models import Q
# Create your views here.

# 영화 데이터 수집
def movieCollect(request):

    api_key = '560c0e0b21628cdf0431b39687354675'
    TMDB_URL = 'https://api.themoviedb.org/3/discover/movie'
    
    # 10페이지 정보 받아오기
    for n in range(1, 11):
        num = str(n)
        Movies_URL = f"{TMDB_URL}?api_key={api_key}&language=ko-KR&page={num}" 
        listData = requests.get(Movies_URL).json()
        resDatas = listData['results']
    
        # 한 영화당 detail정보 가져오기
        for resData in resDatas:
            api_key = '560c0e0b21628cdf0431b39687354675'
            Movie_URL = 'https://api.themoviedb.org/3/movie'
            tmd_id = resData.get('id')
            DETAIL_URL = f"{Movie_URL}/{tmd_id}?api_key={api_key}&language=ko-KR"
            detailData = requests.get(DETAIL_URL).json()

            # 배우, 감독 정보 가져오기
            CREDITS_URL = f"{Movie_URL}/{tmd_id}/credits?api_key={api_key}"
            creditsData = requests.get(CREDITS_URL).json()
            # 배우 찾기
            castData = requests.get(CREDITS_URL).json().get('cast')
            casts = []
            for n in range(len(castData)):
                casts.append(castData[n].get('name'))
                if len(casts) > 4:
                    break
            casts = (', ').join(casts)
            
            # 감독 찾기
            crewData = creditsData.get('crew')
            for n in range(len(crewData)):
                if crewData[n].get('job') =='Director':
                    director = crewData[n].get('name')
                    break
                else:
                    director = ""
                   
            # 장르이름 저장하기
            genres = []
            for genre in detailData.get('genres'):
                genres.append(genre.get('name'))
            genres = (', ').join(genres)
            
            # 배경이미지 없을 경우 오류 발생 방지
            if resData.get('backdrop_path'):
                backdrop_path = "https://image.tmdb.org/t/p/original" + resData.get('backdrop_path')
            

            Movie.objects.get_or_create(
                tmd_id = tmd_id,
                title = resData.get('title'),
                backdrop_path = backdrop_path,
                poster_path = "https://image.tmdb.org/t/p/original"+ resData.get('poster_path'),
                overview = detailData.get('overview'),
                release_date = detailData.get('release_date'),
                tagline = detailData.get('tagline'),
                casts = casts,
                director = director,
                genres = genres,
                popularity = detailData.get('popularity'),
                vote_average = detailData.get('vote_average'),
                )

    return redirect('movies:main')


def main(request):
    # Pagination
    movie_list = Movie.objects.all()
    
    paginator = Paginator(movie_list, 20) 
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'movies': movie_list,
        'page_obj': page_obj,
    }
    return render(request, 'movies/main.html', context)
    
    
# 디테일 페이지
def detail(request, id):
    # 영화
    movie = Movie.objects.get(id=id)
    # 리뷰
    reviews = movie.review_set.all()
    # 평점
    ratings = 0
    for score in movie.score_set.all():
        ratings += score.rating
    if ratings == 0:
        ratingAvg = 0
    else:
        ratingAvg = ratings/movie.score_set.all().count()
    ratingAvg = round(ratingAvg,2)

    YOUTUBE_API_KEY='AIzaSyCPSTJXHRJCuhiH16LYXvsFYYKxTSkAzWw'
    
    YOUTUBE_URL = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'key': YOUTUBE_API_KEY,
        'part': 'snippet',
        'type': 'video',
        'q': movie.title + 'trailer'
    }
    response = requests.get(YOUTUBE_URL, params=params).json()
    # print(response)
    video_id = response['items'][0]['id']['videoId']
    # print(video_id)
    video = f'https://www.youtube.com/embed/{video_id}'

    context = {
        'movie':movie,
        'reviews': reviews, 
        "ratingAvg":ratingAvg,
        'video': video,
    }

    return render(request, 'movies/detail.html', context )

    
# 평점 등록하기
@login_required
def scoreCreate(request, id):
    rating = request.POST.get('rating')
    user = request.user
    movie = Movie.objects.get(id=id)
    score_list = Score.objects.filter(user=user,movie=movie)
    
    if score_list:
        score = score_list.update(rating=rating)
    else:
        score = Score.objects.create(user=user, movie=movie, rating=rating)

    return redirect('movies:detail', id)
  
def movie_create(request):
    if request.user.is_superuser:
        if request.method =='POST':
            form = MovieForm(request.POST)
            if form.is_valid():
                movie = form.save()
                return redirect('movies:main')
        else:
            form = MovieForm()
        context = {
            'form':form,
        }
        return render(request, 'movies/form.html', context)

def movie_update(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method =="POST":
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            return redirect('movies:detail', movie.pk)
    else:
        form = MovieForm(instance=movie)
    context = {
        'form': form,
        'movie': movie,
    }
    return render(request, 'movies/form.html', context)


def movie_delete(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    movie.delete()
    return redirect('movies:main')


# 여기
def review_create(request, movie_pk):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, pk=movie_pk)
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.movie_id = movie.pk
                form.save()
                return redirect('movies:detail', movie.pk)
        else:
            form = ReviewForm()
        context = {
            'form': form
        }
        return render(request, 'movies/form.html', context)
    else:
        return redirect('accounts:login')

def review_detail(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    comments = review.comment_set.all()
    form = CommentForm()
    context = {
        'movie': movie,
        'review': review,
        'form': form,
        'comments':comments,
    }
    return render(request, 'movies/review_detail.html', context)


def review_update(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method =="POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('movies:review_detail', movie_pk, review_pk)
    else:
        form = ReviewForm(instance=review)
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'movies/form.html', context)


def review_delete(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    review.delete()
    return redirect('movies:detail', movie_pk)


def comment_create(request, movie_pk, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.review_id = review.pk
                form.save()
        return redirect('movies:review_detail', movie_pk, review.pk)
    else:
        return redirect('accounts:login')

@require_POST
def comment_delete(request, movie_pk, review_pk, comment_pk):
    if request.method=="POST":
        comment = Comment.objects.get(pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
    return redirect('movies:review_detail', movie_pk, review_pk)


def recommend2(request):
    user = request.user
    movies = Movie.objects.order_by('-popularity')
    result = movies
    api_key = '560c0e0b21628cdf0431b39687354675'
    result2 = []

    if request.user.is_authenticated:
        like_list = []
        like_genres_list = []
        for like_movie in Score.objects.filter(user=user, rating__gte=4).order_by('-rating'):
            id = like_movie.movie
            like_list.append(id)     
            like_genres = id.genres.split(', ')
        like_genres_list.extend(like_genres)

        result_title = []
        for genre in like_genres_list:
            for movie in movies:
                if genre in movie.genres and movie not in like_list and movie.title not in result_title:
                    result2.append(movie)
                    result_title.append(movie.title)

    recommend_URL = f'https://api.themoviedb.org/3/movie/{like_list[-1].tmd_id}/recommendations?api_key={api_key}&language=ko-KR&page=1'
    recommend_list = requests.get(recommend_URL).json()['results']
    recommend_movies = []
    recommend_title = []

    for recommend_movie in recommend_list:
        for movie in movies:
            if recommend_movie['title'] == movie.title and movie.title not in recommend_title:
                recommend_movies.append(movie)
                recommend_title.append(movie.title)



    like_movies1 = result2[:4]
    like_movies2 = result2[4:8]
    like_movies3 = result2[8:12]

    rec_movies1 = recommend_movies[:4]
    rec_movies2 = recommend_movies[4:8]
    # rec_movies3 = recommend_movies[8:12]

    like_movie = like_list[-1]


    context = {
        'like_movies1' : like_movies1,
        'like_movies2' : like_movies2,
        'like_movies3' : like_movies3,
        'rec_movies1' : rec_movies1,
        'rec_movies2' : rec_movies2,
        # 'rec_movies3' : rec_movies3,
        'like_list': like_list, 
        'like_movie': like_movie,
        'like_genres_list': like_genres_list,
    }
    return render(request, 'movies/recommend.html', context)

def profile(request):
    user = request.user
    my_rates = Score.objects.filter(user=user)
    my_rates_list = []
    my_scores_list = []

    for my_rate in my_rates:
        my_rates_list.append((my_rate.movie, my_rate.rating))
    
    for my_score_list in my_rates:
        my_scores_list.append(my_score_list.rating)


    context = {
        'my_scores_list' : my_scores_list,
        'my_rates_list' : my_rates_list,
        'user' : user,
    }
    print(my_scores_list)
    print(1231283213123)

    return render(request, 'movies/profile.html', context)

def user_management(request):
    users = get_user_model().objects.all()
    context = {
        'users' : users,
    }

    return render(request, 'movies/user_management.html', context)

def search_result(request):
    movies = None
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        movies = Movie.objects.all().filter(Q(title__contains=query) | Q(overview__contains=query))
    context = {
        'query': query,
        'movies': movies,
    }
    return render(request, 'movies/search_result.html', context)  