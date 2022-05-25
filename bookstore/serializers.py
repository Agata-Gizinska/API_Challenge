"""
This module provides serializers for Bookstore models.
"""

from rest_framework import serializers
from .models import Author, Book


class AuthorSerializer(serializers. ModelSerializer):
    """
    A class for Author serializer.
    """
    class Meta:
        model = Author
        fields = ['id', 'name']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    """
    A class for Book serializer.
    """
    authors = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'external_id', 'title', 'authors', 'acquired',
                  'published_year', 'thumbnail']
        read_only_fields = ['id']

    def get_authors(self, obj):
        """A method for getting Author objects' names."""
        return [str(author) for author in obj.authors.all()]
