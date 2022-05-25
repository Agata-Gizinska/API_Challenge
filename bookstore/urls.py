from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api_spec/', views.APISpec.as_view(), name='api-spec'),
    path('books/', views.Books.as_view(), name='books'),
    path('books?<query>/', views.Books.as_view(), name='book-filtered'),
    path('books/<int:id>/', views.BookDetails.as_view(), name='books-details'),
    path('import/', views.ImportBooks.as_view(),
         name='bookstore-import-books'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
