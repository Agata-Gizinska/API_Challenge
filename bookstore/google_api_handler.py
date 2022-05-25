"""
This module provides functions for fetching books' information from
Google Books API and parsing them info Bookstore database models.
"""

import json
import requests
from api_challenge.settings import google_books
from .models import Author, Book
from . import book_queries


def fetch_books(author, google_books_url=google_books):
    """
    This function imports data about books for requested author from Google
    Books API.
    """
    url = f"{google_books_url}/books/v1/volumes?q=+inauthor:{author}"
    response = requests.get(url).text
    google_books_data = json.loads(response)

    return google_books_data


def parse_google_books_into_db(google_books_data):
    """
    This function processes and formats given data, creates Book models
    based on these data and returns the number of imported books as
    a dictionary.
    """
    for entry in google_books_data['items']:
        image_links = entry['volumeInfo'].get('imageLinks')
        thumbnail = image_links["thumbnail"] if image_links else None
        info = {"external_id": entry.get("id"),
                "title": entry['volumeInfo'].get("title"),
                "authors": entry['volumeInfo'].get("authors"),
                "published_year": entry['volumeInfo'].get(
                    "publishedDate")[0:4],
                "thumbnail": thumbnail
                }
        if info['authors']:
            for author in info['authors']:
                try:
                    Author.objects.filter(name=author).first().name
                except AttributeError:
                    new_author = Author(name=author)
                    new_author.save()
            authors_list = [Author.objects.filter(name=author).first() for
                            author in info['authors']]
        book = Book.objects.filter(external_id=info['external_id']).first()
        if book:
            # filter by external_id, if matches overwrite all fields
            book.external_id = info['external_id']
            book.title = info['title']
            book.published_year = info['published_year']
            book.thumbnail = info['thumbnail']
            book.authors.clear()  # reset all data about authors
            for author in authors_list:
                book.authors.add(author.id)
        else:
            query = book_queries.get_books_by_authors(authors=authors_list)
            book = query.filter(title=info['title'],
                                published_year=info['published_year']).first()
            if book:
                # update manually inserted book
                book.external_id = info['external_id']
                book.thumbnail = info['thumbnail']
            else:
                # create entirely new book
                book = Book(external_id=info['external_id'],
                            title=info['title'],
                            published_year=info['published_year'],
                            thumbnail=info['thumbnail'])
                # Book instance needs to have a value for field "id"
                # before this many-to-many relationship can be used
                book.save()
                for author in authors_list:
                    book.authors.add(author.id)
        book.save()

    counter = {
        "imported": len(google_books_data['items'])
    }

    return counter
