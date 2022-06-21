"""
A module for custom exceptions.
"""
from rest_framework.exceptions import APIException


class InvalidId(APIException):
    """An class for handling exceptions caused by invalid
    book id."""
    status_code = 404
    default_detail = "There is no book with requested id."
    default_code = "invalid_id"
