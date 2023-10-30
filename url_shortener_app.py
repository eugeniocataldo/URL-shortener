from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import string, random

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
# Initialize all database tables
Base.metadata.create_all(engine)


def generate_short_url():

    while True:
        characters = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(characters) for _ in range(6))

        
        #TODO: Add a check that the short_url is not in the database yet
        url_existing = False
        if not url_existing: 
            return short_url
        

# def shorten_url():
    


@app.route('/shorten', methods=['GET', 'POST'])
def shorten_url():

    data = request.get_json()
    long_url = data.get('url')

    if not long_url:
        return jsonify({'error': "URL is required, please make sure there is an element called 'url' in the JSON you're passing"}), 400
    
    short_url = generate_short_url()
    
    #TODO: Add a check whether the URL is in the database
    
    # Add the URL to my database
    session = Session()
    session.add(UrlMapping(short_url=short_url, long_url=long_url))
    session.commit()
    session.close()

    return jsonify({'long_url': long_url}), 201





app.run()
