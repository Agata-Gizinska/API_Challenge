"""
This module provides functions for filtering the Bookstore database
and acquiring Book objects.
"""


from django.http import Http404
from django.db.models import Count
from .models import Book


def filter_books(**kwargs):
    """
    This function filters given keyword arguments
    """
    book_filter = {}
    if 'id' in kwargs:
        book_filter['id__exact'] = int(kwargs['id'])
    if 'external_id' in kwargs:
        book_filter['external_id__exact'] = kwargs['external_id']
    if 'from' in kwargs:
        book_filter['published_year__gte'] = int(kwargs['from'])
    if 'to' in kwargs:
        book_filter['published_year__lte'] = int(kwargs['to'])
    if 'published_year' in kwargs:
        book_filter['published_year__exact'] = int(kwargs['published_year'])
    # filtering by a list of authors is ommited, because queries with authors
    # are executed by get_books_by_authors
    if 'author' in kwargs:
        book_filter['authors__name__icontains'] = kwargs['author'].strip('"')
    if 'authors' in kwargs:
        if isinstance(kwargs['authors'], str):
            kwargs['authors'].strip('"')
            book_filter['authors__name__icontains'] = kwargs['authors']
    if 'title__icontains' in kwargs:
        book_filter['title__icontains'] = kwargs['title__icontains'].strip('"')
    if 'title__exact' in kwargs:
        book_filter['title__exact'] = kwargs['title__exact'].strip('"')
    if 'acquired' in kwargs:
        if isinstance(kwargs['acquired'], str):
            kwargs['acquired'].lower()
        book_filter['acquired'] = kwargs['acquired'] == 'true'

    return Book.objects.filter(**book_filter)


def get_books(data, method):
    """
    Filter database for multiple books.
    """
    # Get books by performing filtering by book's title
    if 'title' in data:
        # Filter for exact title only for POST /books/
        if data['title'] and method == 'exact':
            data['title__exact'] = data['title']
            data.pop('title')
            # Don't filter by 'acquired' status, because if all other
            # parameters match the book in database, a PATCH /books/123
            # request is more appropriate than adding an additional
            # entry in the database. However, save a copy in 'acquired
            # _status" to use it when returning data
            if 'acquired' in data:
                data['acquired_status'] = data['acquired']
                data.pop('acquired')
        # Filter for books containing the given phrase in the title
        elif data['title'] and not method:
            data['title__icontains'] = data['title']
            data.pop('title')
    # Get books by other parameters
    if data:
        books = filter_books(**data)
        return books
    # Get the whole list of books (no filters)
    books = Book.objects.all()

    return books


def get_book_details(requested_id):
    """
    Return Book object for requested id or Http404.
    """
    book = filter_books(id=requested_id['id']).first()
    if book:
        return book
    else:
        return Http404


def get_books_by_authors(authors, queryset=Book.objects):
    """
    Filter queryset for a book with multiple prompted authors.
    """
    queryset.annotate(count=Count('authors'))

    for author in authors:
        queryset = queryset.filter(authors__name=author)

    return queryset
