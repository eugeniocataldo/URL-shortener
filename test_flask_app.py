import sys
import os
import pytest
import json
import re


# Add the path to your application package to sys.path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from url_shortener_app import app, UrlMapping, Session

# Or
from url_shortener_app import app, UrlMapping, Session

@pytest.fixture
def app_context():
    with app.app_context():
        yield


def generate_new_url(field_name):

    # Generate an URL and check that it's unique (in the extreme case someone saved a URL like "test")
    session = Session()
    my_string = "test"
    while True:
        if field_name == "long_url":
            already_in_db = session.query(UrlMapping).filter_by(long_url=my_string).first()
        elif field_name == "short_url":
            already_in_db = session.query(UrlMapping).filter_by(short_url=my_string).first()
        else:
            raise ValueError("Invalid field_name specified")
        
        if not already_in_db:
            session.close()
            break
        my_string += "test"

    return my_string



def test_shorten_existing_url(app_context):

    client = app.test_client()

    test_data = {"url": "https://example.com/initial-url"} # For how the app is defined, this is always in the database

    # Send a POST request with the test data
    response = client.post('/shorten', data=json.dumps(test_data), content_type='application/json')

    assert response.status_code == 303
    response_data = json.loads(response.data)
    assert 'Location' in response_data
    assert response_data['Location'] == "/urls/initial"

def test_shorten_new_url():

    client = app.test_client()

    my_string = generate_new_url(field_name="long_url")

    test_data = {"url": my_string}

    # Send a POST request with the test data
    response = client.post('/shorten', data=json.dumps(test_data), content_type='application/json')

    session = Session()
    session.query(UrlMapping).filter_by(long_url=my_string).delete()
    session.commit()
    session.close()

    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'Location' in response_data
    assert re.match((r"/urls/[a-zA-Z0-9]{6}"), string=response_data["Location"])


def test_shorten_no_url_provided():

    client = app.test_client()

    test_data = {"wrong": "Some gibberish"}

    # Send a POST request with the test data
    response = client.post('/shorten', data=json.dumps(test_data), content_type='application/json')

    assert response.status_code == 400


def test_stats_existing_url():

    client = app.test_client()

    response = client.get('urls/initial/stats')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert isinstance(response_data['hits'], int)
    assert response_data["url"] == "https://example.com/initial-url"
    assert response_data["created_on"]


def test_stats_non_existing_url():

    client = app.test_client()

    my_string = generate_new_url(field_name="short_url")

    response = client.get("urls/" + my_string + "/stats")

    assert response.status_code == 404


def test_shortcode_existing_url():

    client = app.test_client()

    response = client.get('urls/initial')

    assert response.status_code == 307
    response_data = json.loads(response.data)
    assert response_data["Location"] == "https://example.com/initial-url"


def test_shortcode_non_existing_url():

    client = app.test_client()

    my_string = generate_new_url(field_name="short_url")

    response = client.get("urls/" + my_string)

    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert response_data["Error"]
    assert response_data["Message"]

        


if __name__ == '__main__':
    pytest.main()