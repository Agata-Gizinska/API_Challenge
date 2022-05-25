"""
This module provides models for Bookstore database.
"""

from django.db import models


class Author(models.Model):
    """
    A model for Author objects.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class Book(models.Model):
    """
    A model for Book objects.
    """
    id = models.AutoField(primary_key=True)
    external_id = models.CharField(max_length=200, null=True)
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    acquired = models.BooleanField(default=False)
    published_year = models.IntegerField()
    thumbnail = models.URLField(null=True)

    def __str__(self):
        return str(self.title)
