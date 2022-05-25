"""
This module provides functions and classes for all Bookstore views.
"""

import json
from django.http import Http404
from django.shortcuts import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from api_challenge.settings import app_version
from .serializers import BookSerializer
from .google_api_handler import fetch_books, parse_google_books_into_db
from .book_queries import get_books, get_book_details


def home(request):
    """A simple function for redirecting user to page contents."""
    return HttpResponseRedirect('/books')


class ImportBooks(APIView):
    """
    A class for POST /import view.
    """
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        A method for POST requests.
        """
        data = json.loads(request.body)
        author = data['author']
        google_books_data = fetch_books(author)
        counter = parse_google_books_into_db(google_books_data)
        return Response(counter)


class APISpec(APIView):
    """
    A class for GET /api_spec view.
    """
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """
        A method for GET requests.
        """
        return Response(app_version)


# GET /books
# POST /books
class Books(generics.ListCreateAPIView):
    """
    A class for GET /books and POST /books view.
    """
    serializer_class = BookSerializer
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """A method for GET requests."""
        books = get_books(request.query_params.dict(), method=None)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        """A method for POST requests."""
        data = json.loads(request.body)
        book = get_books(data, method='exact')
        # Check if book is in the database to avoid doubles
        if book:
            if 'acquired_status' in data:
                response = {
                    "message": "Use PATCH request to update 'acquired' status"
                    }
                return Response(response)
            response = {
                "message": "This book is already in the database"
            }
            return Response(response)
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetails(generics.RetrieveUpdateDestroyAPIView):
    """
    A class for GET, PATCH and DELETE /books/<id> view.
    """
    serializer_class = BookSerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        """A method for GET /books/<id>."""
        book = get_book_details(kwargs)
        if book == Http404:
            response = {
                "message": f"There is no book with id {kwargs['id']}"
            }
            return Response(response)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """A method for PATCH /books/<id>."""
        book = get_book_details(kwargs)
        if book == Http404:
            response = {
                "message": f"There is no book with id {kwargs['id']}"
            }
            return Response(response)
        updated_value = request.data
        book.acquired = updated_value.get('acquired')
        book.save()
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """A method for DELETE /books/<id>."""
        instance = get_book_details(kwargs)
        if instance == Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        """A method for performing destroy on instance."""
        instance.authors.clear()
        instance.delete()
