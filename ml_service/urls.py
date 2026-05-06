from django.urls import path
from . import views

urlpatterns = [
    path('suggest-category/', views.SuggestCategoryView.as_view(), name='suggest-category'),
    path('batch-suggest/', views.BatchSuggestCategoriesView.as_view(), name='batch-suggest'),
    path('train-model/', views.TrainModelView.as_view(), name='train-model'),
    path('accept-suggestion/', views.AcceptSuggestionView.as_view(), name='accept-suggestion'),
]