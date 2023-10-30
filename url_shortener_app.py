from flask import Flask, request, render_template
import pandas as pd
import string, random

app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
def rootpage():

    url = ''

    if request.method == 'POST' and 'url' in request.form:
        url = request.form.get('url')


    return render_template("shorten_url.html",
                           input_url=url)
def generate_short_url():

    while True:
        characters = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(characters) for _ in range(6))

        
        #TODO: Add a check that the short_url is not in the database yet
        url_existing = False
        if not url_existing: 
            return short_url
        

app.run()

# @app.route('/shorten', methods=['GET', 'POST'])
# def shorten_page():