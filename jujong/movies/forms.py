from django import forms
from .models import Movie, Comment, Score, Review

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
        
class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields = ['content',]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'rank', 'content']

class SearchForm(forms.ModelForm):
    word = forms.CharField(label='Search Word')