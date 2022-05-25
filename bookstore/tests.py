import json
from unittest.mock import patch
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from .models import Author, Book
from .serializers import BookSerializer

with open('bookstore/sample_database.json', 'r', encoding='utf-8') as spl_db:
    sample_database = json.loads(spl_db.read())

with open('bookstore/sample_google_response.json', 'r', encoding='utf-8') as s:
    sample_google_response = json.loads(s.read())


class TestEndpoints(APITestCase):
    """
    A class for testing all endpoints.
    """
    def setUp(self):
        """This function prepares an API Client and sample models for tests."""
        self.client = APIClient()
        for book in sample_database:
            authors_list = book['authors']
            new_book = Book(external_id=book['external_id'],
                            title=book['title'],
                            published_year=book['published_year'],
                            acquired=book['acquired'],
                            thumbnail=book['thumbnail'])
            new_book.save()
            for author in authors_list:
                author_obj = Author(name=author)
                author_obj.save()
                new_book.authors.add(author_obj.id)

    def test_get_api_spec(self):
        """This function tests GET /api_spec endpoint."""
        url = reverse('api-spec')
        response = self.client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data['info'], dict)
        assert isinstance(response.data['info'].get('version'), str)
        assert response.data['info'].get('version') == '2022.05.16'

    def test_get_request_books(self):
        """This function tests GET /books endpoint."""
        url = reverse('books')
        books = Book.objects.all()
        expected_data = BookSerializer(books, many=True).data
        response = self.client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert response.data == expected_data

    def test_post_request_books_new(self):
        """This function tests POST /books endpoint when the specified
        Book object does not exist in the database."""
        test_data = {
            "title": "Opowiadania 2",
            "authors": ["Martyna Nowak"],
            "acquired": False,
            "published_year": 2020,
        }
        url = reverse('books')
        response = self.client.post(url, test_data, format='json')
        assert response.status_code == 201

    def test_post_request_books_doubled_parameters(self):
        """This function tests POST /books endpoint when trying to add
        a doubling Book object into the database."""
        test_data = {
            "title": "Opowiadania",
            "authors": [
                "Marek Nowak"
            ],
            "published_year": 2021,
        }
        expected_response = {
                "message": "This book is already in the database"
            }
        url = reverse('books')
        response = self.client.post(url, test_data, format='json')
        assert response.status_code == 200
        assert response.data == expected_response

    def test_post_request_books_acquire_change(self):
        """This function tests POST /books endpoint for preventing updates
        of 'acquired' parameter using POST instead of PATCH."""
        test_data = {
            "title": "Opowiadania",
            "authors": [
                "Marek Nowak"
            ],
            "acquired": True,
            "published_year": 2021,
        }
        expected_response = {
            "message": "Use PATCH request to update 'acquired' status"
            }
        url = reverse('books')
        response = self.client.post(url, test_data, format='json')
        assert response.status_code == 200
        assert response.data == expected_response

    def test_get_request_book(self):
        """This function tests GET /books/<id> endpoint."""
        test_data = {"id": 2}
        url = f"/books/{test_data['id']}/"
        response = self.client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data, dict)
        assert not response.data['external_id']

    def test_patch_request_book(self):
        """This function tests PATCH /books/<id> endpoint."""
        test_data = {"id": 2}
        url = f"/books/{test_data['id']}/"
        response = self.client.patch(url, data={"acquired": True})
        assert response.status_code == 200
        assert isinstance(response.data, dict)
        assert response.data['acquired']

    def test_delete_request_book(self):
        """This function tests DELETE /books/<id> endpoint."""
        test_author = Author(name="Frank Joker")
        test_author.save()
        test_book = Book(title="Funny stories", published_year=2022)
        test_book.save()
        test_book.authors.add(test_author.id)
        number_of_books_before_del = len(Book.objects.all())
        number_of_authors_before_del = len(Author.objects.all())
        url = f'/books/{test_book.id}/'
        response = self.client.delete(url)
        number_of_books_after_del = len(Book.objects.all())
        number_of_authors_after_del = len(Author.objects.all())
        assert response.status_code == 204
        assert number_of_books_before_del > number_of_books_after_del
        assert number_of_authors_before_del == number_of_authors_after_del

    @patch("bookstore.views.fetch_books")
    def test_post_import_books(self, mock_fetch_books):
        """This function tests POST /import endpoint."""
        url = reverse('bookstore-import-books')
        data = json.dumps({
            "author": "Nowak"
        })
        mock_fetch_books.return_value = sample_google_response
        response = self.client.post(url, data, content_type='application/json')

        assert response.status_code == 200
        assert isinstance(response.data, dict)
        assert isinstance(response.data['imported'], int)
