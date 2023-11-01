# URL Shortener App

The URL Shortener App is a simple web application built with Flask, Python, and SQLite that allows users to shorten long URLs into unique, easy-to-share shortcodes. This `README.md` file provides an overview of the app, its features, and instructions for running it.

## Features

List of features:
- Shorten long URLs to unique shortcodes.
- Retrieve statistics for a shortened URL, including hit count and creation date.
- Redirect users from shortcodes to the original long URLs.
- Handle error cases, including invalid URLs and non-existing shortcodes.
- Data storage using SQLite database.
- Easily extendable for additional features and improvements.

## Endpoints

The server has 3 endpoints:
* `/shorten`, which accepts a POST request to shorten a URL and store it in a database

   Example request:

      ```http
      POST /shorten
      Content-Type: application/json

      {"url": "https://example.com/your-long-url"}

* `/urls/<short_url>`, which accepts a GET request and redirect to the long URL related to the shortened input


   Example request:

      ```http
      GET /urls/<shortcode>

* `/urls/<short_url>/stats`, which returns hit count, long URL, and created date for the shortened URL

   Example request:

      ```http
      GET /urls/<shortcode>/stats

## Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- SQLite (comes pre-installed with Python)

## Installation

1. Clone the repository to your local machine:

   ```shell
   git clone https://github.com/your-username/url-shortener-app.git

2. Navigate to the app's directory:

   ```shell
   cd url-shortener-app

3. Install the required Python packages (using conda):

   ```shell
    conda create --name myenv python=3.11
    conda activate myenv
    conda install --file requirements.txt


## Usage

1. Start the Flask development server

python url_shortener_app.py

2. Access the app in your web browser at http://localhost:5000.

3. Use the following endpoints to interact with the app:
   * Shorten a URL:

      ```shell
      POST /shorten
      Content-Type: application/json

      {"url": "https://example.com/your-long-url"}
   
   * Retrieve statistics for a shortened URL:
      ```shell
      GET /urls/<shortcode>/stats

   * Redirect to the original long URL using the shortcode:
      ```shell
      GET /urls/<shortcode>



