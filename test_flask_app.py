import sys
import os
import pytest
import json
import re
from url_shortener_app import app, UrlMapping, Session


def generate_new_url(field_name):
    """
    Generate a new unique URL.

    This function generates a new URL, ensuring its uniqueness by checking
    against the provided 'field_name' in the database. It appends 'test' to
    the base string until a unique URL is found.

    Parameters:
    - field_name (str): The field name to check for uniqueness ('long_url' or 'short_url').

    Returns:
    - str: A unique URL.
    """

    # Generate an URL and check that it's unique (in the extreme case someone saved a URL like "test")
    session = Session()
    my_string = "test"

    # Start a loop to check if the sample string is already in and, if yes, change it until it's unique
    while True:
        # Small logic to search over different fields in the database
        if field_name == "long_url":
            already_in_db = session.query(UrlMapping).filter_by(
                long_url=my_string).first()
        elif field_name == "short_url":
            already_in_db = session.query(UrlMapping).filter_by(
                short_url=my_string).first()
        else:
            raise ValueError("Invalid field_name specified")

        # Once string is not in database, close session and get out of loop
        if not already_in_db:
            session.close()
            break
        
        # Edit string if it's already in the database
        my_string += "test"

    return my_string


def test_shorten_existing_url():
    """
    Test the behavior of shortening an existing URL.

    This test sends a POST request to the '/shorten' endpoint with a URL
    that is already in the database. It checks that the response status
    code is 303 (See Other) and verifies that the 'Location' field in the
    response data matches the expected URL for the existing mapping.
    """

    # Start a test session
    client = app.test_client()

    # For how the app is defined, this is always in the database
    test_data = {"url": "https://example.com/initial-url"}

    # Send a POST request with the test data
    response = client.post(
        '/shorten', data=json.dumps(test_data), content_type='application/json')

    assert response.status_code == 303
    response_data = json.loads(response.data)
    assert 'Location' in response_data
    assert response_data['Location'] == "/urls/hardcoded_entry_do_not_modify"


def test_shorten_new_url():
    """
    Test the behavior of shortening a new URL.

    This test sends a POST request to the '/shorten' endpoint with a new URL that
    is not in the database. It checks that the response status code is 201 (Created)
    and verifies that the 'Location' field in the response data matches the expected
    URL format, which includes a unique shortcode.
    """

    # Start a test session
    client = app.test_client()

    # Craft a URL that is not in the database
    my_string = generate_new_url(field_name="long_url")
    test_data = {"url": my_string}

    # Send a POST request with the test data
    response = client.post(
        '/shorten', data=json.dumps(test_data), content_type='application/json')

    # Delete the URL from the database after use, not to modify it with this test
    session = Session()
    session.query(UrlMapping).filter_by(long_url=my_string).delete()
    session.commit()
    session.close()

    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'Location' in response_data
    assert re.match((r"/urls/[a-zA-Z0-9]{6}"),
                    string=response_data["Location"])


def test_shorten_no_url_provided():
    """
    Test the behavior of shortening when no URL is provided.

    This test sends a POST request to the '/shorten' endpoint without providing
    a valid 'url' field in the request JSON data. It checks that the response status
    code is 400 (Bad Request), indicating that the request is invalid due to
    the absence of a required 'url' field.
    """
    # Start a test session
    client = app.test_client()

    # Craft a JSON without a 'url' field
    test_data = {"wrong": "Some gibberish"}

    # Send a POST request with the test data
    response = client.post(
        '/shorten', data=json.dumps(test_data), content_type='application/json')

    assert response.status_code == 400


def test_stats_existing_url():
    """
    Test retrieving statistics for an existing URL.

    This test sends a GET request to the '/urls/<shortcode>/stats' endpoint for
    an existing URL (with a hardcoded shortcode for testing). It checks that
    the response status code is 200 (OK) and verifies the format and content of
    the response data.
    """
    # Start a test session
    client = app.test_client()

    # Send GET request with existing URL
    response = client.get('urls/hardcoded_entry_do_not_modify/stats')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert isinstance(response_data['hits'], int)
    assert response_data["url"] == "https://example.com/initial-url"
    assert response_data["created_on"]


def test_stats_non_existing_url():
    """
    Test retrieving statistics for a non-existing URL.

    This test sends a GET request to the '/urls/<shortcode>/stats' endpoint for
    a URL that does not exist in the database (with a dynamically generated shortcode).
    It checks that the response status code is 404 (Not Found).
    """

    # Start a test session
    client = app.test_client()
    
    # Craft a short URL that is not in the database
    my_string = generate_new_url(field_name="short_url")

    # Send GET request with non-existent short URL
    response = client.get("urls/" + my_string + "/stats")

    assert response.status_code == 404


def test_shortcode_existing_url():
    """
    Test the behavior of accessing an existing URL's shortcode.

    This test sends a GET request to the '/urls/<shortcode>' endpoint for
    an existing URL (with a hardcoded shortcode for testing). It checks
    that the response status code is 307 (Temporary Redirect) and verifies
    that the 'Location' field in the response data matches the expected URL.
    """
    # Start a test session
    client = app.test_client()

    # Send GET request to existing short URL
    response = client.get('urls/hardcoded_entry_do_not_modify')

    assert response.status_code == 307
    response_data = json.loads(response.data)
    assert response_data["Location"] == "https://example.com/initial-url"


def test_shortcode_non_existing_url():
    """
    Test the behavior of accessing a shortcode for a non-existing URL.

    This test sends a GET request to the '/urls/<shortcode>' endpoint for a URL
    that does not exist in the database (with a dynamically generated shortcode).
    It checks that the response status code is 404 (Not Found).
    """

    # Start a test session
    client = app.test_client()

    # Craft a URL that is not in the database
    my_string = generate_new_url(field_name="short_url")

    # Send GET request with the non-existent short URL
    response = client.get("urls/" + my_string)

    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert response_data["Error"]
    assert response_data["Message"]


if __name__ == '__main__':
    pytest.main()
