from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine, Column, Integer, String, select
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
        # Generate a random 6-characters string
        characters = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(characters) for _ in range(6))

        # Check whether the shortened URL is unique or is already present in the database
        session = Session()
        url_already_exists  = session.query(UrlMapping).filter_by(short_url=short_url).first()

        if url_already_exists: 
            continue # If already present, generate a new one

        session.close()
            
        return short_url
    

@app.route('/shorten', methods=['GET', 'POST'])
def shorten_url():

    data = request.get_json()
    input_url = data.get('url')

    if not input_url:
        return jsonify({'error': "URL is required, please make sure there is an element called 'url' in the JSON you're passing"}), 400
    
    # Check if the long URL is already in the database and, if yes, return the corresponding shortened URL
    session = Session()
    url_already_mapped = session.query(UrlMapping).filter_by(long_url=input_url).first()

    if url_already_mapped:
        session.close()
        return jsonify({'Location': "/urls/{}".format(url_already_mapped.short_url)}), 303
        
    
    # Add URL to my database
    short_url = generate_short_url()
    session.add(UrlMapping(short_url=short_url, long_url=input_url))
    session.commit()
    session.close()

    return jsonify({'Location': "/urls/{}".format(short_url)}), 201





app.run()
