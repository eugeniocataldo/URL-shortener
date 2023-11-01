from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import string
import random
import datetime

app = Flask(__name__)

# Choose which database to use
DATABASE_URL = 'sqlite:///url_database.db'

# Create engine and session factory using the chosen database
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Define database structure
Base = declarative_base()


class UrlMapping(Base):
    __tablename__ = 'url_mapping'
    id = Column(Integer, primary_key=True)
    short_url = Column(String)
    long_url = Column(String)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    hit_count = Column(Integer, default=0)


# Initialize all database tables
Base.metadata.create_all(engine)

# If the database is just created, add an initial entry (used for testing)
session = Session()
initial_entry = UrlMapping(short_url="hardcoded_entry_do_not_modify",
                           long_url="https://example.com/initial-url")
initial_entry_already_in = session.query(UrlMapping).filter_by(
    long_url="https://example.com/initial-url").first()

if not initial_entry_already_in:
    session.add(initial_entry)
    session.commit()

session.close()


def generate_short_url():
    """Generate a unique 6-characters URL

    This function generates a random 6-characters short URL, with both numbers and digits. 
    It also checks in our database to make sure that the randomly generated URL is unique

    Returns:
        short_url (str): randomly-generated short URL
    """

    while True:
        # Generate a random 6-characters string
        characters = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(characters) for _ in range(6))

        # Check whether the shortened URL is unique or is already present in the database
        session = Session()
        url_already_exists = session.query(
            UrlMapping).filter_by(short_url=short_url).first()

        if url_already_exists:
            continue  # If already present, generate a new one

        session.close()

        return short_url


@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Shorten a long URL and store it in a database or retrieve the existing shrot URL

    This route accepts a POST request with a JSON payload containing the URL to shorten.
    It checks if the URL is already existent in the database. If it does, it returns the 
    existing short URL. If it doesn't it generates a new short URL, stores it in the database,
    and return it

    Returns:
        response (JSON): A JSON response containing the short URL:
        {"Location": "/urls/<short_url>}

    If the long URL is missing in the request, it returns an error response:
    {'error': "URL is required, please make sure there is an element called 'url' in the JSON you're passing"}

    HTTP Method: POST
    URL: /shorten
    Content-Type: application/json

    Example JSON Payload:
    {
        "url": "https://example.com/oo/bar
    }

    HTTP Status Codes:
    - 201 (Created) if a new short URL is generated
    - 303 (See Other) if the long URL already exists in the database
    - 400 (Bad Request) if no url is provided
    """

    data = request.get_json()
    input_url = data.get('url')

    if not input_url:
        return jsonify({
            'Error': "No URL found",
            "Message": "URL is required, please make sure there is an element called 'url' in the JSON you're passing",
        }), 400

    # Check if the long URL is already in the database and, if yes, return the corresponding shortened URL
    session = Session()
    url_already_mapped = session.query(
        UrlMapping).filter_by(long_url=input_url).first()

    if url_already_mapped:
        session.close()
        return jsonify({'Location': "/urls/{}".format(url_already_mapped.short_url)}), 303

    # If URL is not in the database yet, add it to the database
    short_url = generate_short_url()
    session.add(UrlMapping(short_url=short_url, long_url=input_url))
    session.commit()
    session.close()

    return jsonify({'Location': "/urls/{}".format(short_url)}), 201


@app.route('/urls/<shortcode>/stats', methods=['GET'])
def get_url_stats(shortcode):
    """Retrieves the statistics of a shortened URL

    This route accepts a GET request at the URL: /urls/<short_url>/stats. 
    It checks if the shortened URL is in the database. If it does, it returns
    a statistics about the short URL. If it doesn't it returns an error.

    Args:
        shortcode (str): The shortened URL of which the user wants to check statistics

    Returns:
        response (JSON): a JSON response containing how many times the short URL
        has been visited, the (long) URL it corresponds to, and the day in which 
        the short URL has been created:
        {
            "hits": <hit_count>,
            "url": <long_url>,
            "created_on": <created_date>
        }

        If the short URL provided through <shortcode> is not in the database, 
        it returns an error response, also JSON:
        {"error": "Short URL not found"}

        HTTP Method: GET
        URL: /urls/<shortcode>/stats

        HTTP Status Codes:
        - 200 (OK) if the short URL is in the database
        - 404 (Error) if the short URL is not in the database
    """

    session = Session()

    selected_url = session.query(UrlMapping).filter_by(
        short_url=shortcode).first()

    if selected_url:
        stats = {
            "hits": selected_url.hit_count,
            "url": selected_url.long_url,
            "created_on": selected_url.created_on.isoformat(),
        }
        session.close()
        return jsonify(stats), 200
    else:
        session.close()
        return jsonify({
            "Error": "Short URL not found",
            "Message": "The short URL was not found in the database, please check if it's correct"
        }), 404


@app.route('/urls/<shortcode>', methods=['GET'])
def shortened_url(shortcode):
    """Returns the long URL to which the shortened URL corresponds to

    This route accepts a GET request at the URL: /urls/<shortcode>. 
    It checks if the shortened URL is in the database. If it does, it returns
    the corresponding long URL. If it doesn't it returns an error.

    Args:
        shortcode (str): The shortened URL of which the user wants to check statistics

    Returns:
        response (JSON): a JSON response containing the long URL corresponding to
        the short URL in the request:
        {"Location": "<long_url>"}

        If the short URL provided through <shortcode> is not in the database, 
        it returns an error response, also JSON:
        {"error": "Short URL not present in database, please make sure it's written correctly"}

        HTTP Method: GET
        URL: /urls/<shortcode>

        HTTP Status Codes:
        - 307 (Temporary Redirect) if the short URL is in the database
        - 404 (Error) if the short URL is not in the database
    """

    session = Session()

    selected_url = session.query(UrlMapping).filter_by(
        short_url=shortcode).first()

    if selected_url:
        # Pick out the long URL before updating the session
        long_url = selected_url.long_url
        # Update the hit count of the short URL
        selected_url.hit_count += 1
        session.commit()
        session.close()

        return jsonify({'Location': "{}".format(long_url)}), 307
    else:
        session.close()
        return jsonify({
            "Error": "Short URL not found",
            "Message": "The short URL was not found in the database, please check if it's correct",
        }), 404


# Define custom error handlers

@app.errorhandler(SQLAlchemyError)
def handle_database_error(e):
    response = jsonify({
        "Error": "A database connection error occurred",
        "Message": "Sorry, there was a problem connecting to the database. Please ensure that the database is available and try again."
    })
    response.status_code = 500
    return response


if __name__ == '__main__':
    app.run()
