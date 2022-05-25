# API Challenge

Welcome to my implementation of the requested Bookstore REST API.

Feel free to navigate with

    /               - GET

    books/          - GET, POST

    books/<id>/     - GET, PATCH, DELETE

    import/         - POST


## Installation
<br>

###  With docker

To create image

```docker build -t demo .```

To run the server and listen for http traffic on localhost:80

```docker run -p 80:80 -e PORT=80 demo```
<br><br>
###  Manual
requirements

```python3```

```pip```

use pip to install other reqs

```  pip install -r requirements.txt ```

run server

```python3 manage.py runserver 0.0.0.0:80```
<br><br>
## Currently hosted on Heroku at
=> [bookstore-api-challenge](https://bookstore-api-challenge.herokuapp.com/)