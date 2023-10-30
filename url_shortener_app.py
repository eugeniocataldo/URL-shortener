from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
def rootpage():

    url = ''

    if request.method == 'POST' and 'url' in request.form:
        url = request.form.get('url')


    return render_template("shorten_url.html",
                           input_url=url)



app.run()

# @app.route('/shorten', methods=['GET', 'POST'])
# def shorten_page():