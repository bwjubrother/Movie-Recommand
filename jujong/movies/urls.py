from django.urls import path
from . import views


app_name= "movies"

urlpatterns =[
    path('', views.main, name="main"),
    path('movieCollect/', views.movieCollect, name="movieCollect"),
    path('<int:id>/', views.detail, name="detail"),
    # path('<int:id>/comment/create/',views.commentCreate, name="commentCreate"),
    # path('<int:id>/comments/<int:comment_id>/delete/', views.commentDelete, name='commentDelete'),
    path('<int:id>/score/create/',views.scoreCreate, name="scoreCreate"),
    path('recommend/', views.recommend2, name="recommend2"),
    path('movie_create/', views.movie_create, name='movie_create'),
    path('<int:movie_pk>/update/', views.movie_update, name='movie_update'),
    path('<int:movie_pk>/delete/', views.movie_delete, name='movie_delete'),
    path('<int:movie_pk>/review_create/', views.review_create, name='review_create'),
    path('<int:movie_pk>/<int:review_pk>', views.review_detail, name='review_detail'),
    path('<int:movie_pk>/<int:review_pk>/review_update/', views.review_update, name='review_update'),
    path('<int:movie_pk>/<int:review_pk>/review_delete/', views.review_delete, name='review_delete'),
    path('<int:movie_pk>/<int:review_pk>/comment_create/', views.comment_create, name='comment_create'),
    path('<int:movie_pk>/<int:review_pk>/<int:comment_pk>/comment_delete/', views.comment_delete, name='comment_delete'),
    path('profile/', views.profile, name= "profile"),
    path('user_management/', views.user_management, name = "user_management"),
    path('search/search_result', views.search_result, name="search_result"),



]